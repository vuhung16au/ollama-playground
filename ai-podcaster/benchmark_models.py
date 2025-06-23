import time
import requests
import json
from typing import Dict, List, Optional
import tiktoken
from transformers import AutoTokenizer
import sentencepiece as smp
import statistics
import os
from datetime import datetime
import psutil
import threading
import subprocess
import shutil
import platform

try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    
try:
    import nvidia_ml_py3 as nvml
    NVIDIA_ML_AVAILABLE = True
except ImportError:
    NVIDIA_ML_AVAILABLE = False

class SystemMonitor:
    def __init__(self):
        self.cpu_samples = []
        self.memory_samples = []
        self.gpu_samples = []
        self.monitoring = False
        self.monitor_thread = None
        
        # Initialize GPU monitoring if available
        if NVIDIA_ML_AVAILABLE:
            try:
                nvml.nvmlInit()
                self.gpu_count = nvml.nvmlDeviceGetCount()
                print(f"NVIDIA GPU monitoring initialized. Found {self.gpu_count} GPU(s)")
            except Exception as e:
                print(f"Failed to initialize NVIDIA ML: {e}")
                self.gpu_count = 0
        else:
            self.gpu_count = 0
    
    def start_monitoring(self):
        """Start monitoring system resources"""
        self.monitoring = True
        self.cpu_samples = []
        self.memory_samples = []
        self.gpu_samples = []
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop monitoring and return collected metrics"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        
        metrics = {
            "peak_memory_mb": max(self.memory_samples) if self.memory_samples else 0,
            "avg_cpu_percent": statistics.mean(self.cpu_samples) if self.cpu_samples else 0,
            "max_cpu_percent": max(self.cpu_samples) if self.cpu_samples else 0,
            "avg_gpu_utilization": statistics.mean(self.gpu_samples) if self.gpu_samples else 0,
            "max_gpu_utilization": max(self.gpu_samples) if self.gpu_samples else 0,
        }
        
        return metrics
    
    def _monitor_loop(self):
        """Internal monitoring loop"""
        while self.monitoring:
            try:
                # Get current process
                process = psutil.Process()
                
                # Monitor memory (RSS - Resident Set Size)
                memory_info = process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                self.memory_samples.append(memory_mb)
                
                # Monitor CPU
                cpu_percent = process.cpu_percent()
                self.cpu_samples.append(cpu_percent)
                
                # Monitor GPU if available
                if NVIDIA_ML_AVAILABLE and self.gpu_count > 0:
                    gpu_utilization = self._get_gpu_utilization()
                    if gpu_utilization is not None:
                        self.gpu_samples.append(gpu_utilization)
                
            except Exception as e:
                print(f"Monitoring error: {e}")
            
            time.sleep(0.1)  # Sample every 100ms
    
    def _get_gpu_utilization(self):
        """Get current GPU utilization"""
        try:
            if NVIDIA_ML_AVAILABLE:
                # Get utilization for first GPU (can be extended for multiple GPUs)
                handle = nvml.nvmlDeviceGetHandleByIndex(0)
                utilization = nvml.nvmlDeviceGetUtilizationRates(handle)
                return utilization.gpu
        except Exception as e:
            return None
        return None
    
    def get_model_size(self, model_name: str) -> Dict:
        """Get model size information from Ollama"""
        try:
            # Get model info from Ollama
            response = requests.post(f"http://localhost:11434/api/show", 
                                  json={"name": model_name})
            if response.status_code == 200:
                model_info = response.json()
                # Extract size information if available
                size_bytes = model_info.get("size", 0)
                size_mb = size_bytes / 1024 / 1024 if size_bytes else 0
                size_gb = size_mb / 1024 if size_mb else 0
                
                return {
                    "size_bytes": size_bytes,
                    "size_mb": round(size_mb, 2),
                    "size_gb": round(size_gb, 2),
                    "parameter_count": model_info.get("details", {}).get("parameter_size", "Unknown"),
                    "quantization": model_info.get("details", {}).get("quantization_level", "Unknown")
                }
            else:
                return self._estimate_model_size_fallback(model_name)
                
        except Exception as e:
            print(f"Error getting model size for {model_name}: {e}")
            return self._estimate_model_size_fallback(model_name)
    
    def _estimate_model_size_fallback(self, model_name: str) -> Dict:
        """Fallback method to estimate model size"""
        size_estimates = {
            "1.7b": 1.7, "1.5b": 1.5, "2b": 2.0, "3b": 3.0, "7b": 7.0,
            "mini": 3.8,  # phi3:mini is typically around 3.8B parameters
        }
        
        estimated_params = 0
        for size_key, params in size_estimates.items():
            if size_key in model_name.lower():
                estimated_params = params
                break
        
        # Rough estimate: 2 bytes per parameter for quantized models
        estimated_size_gb = estimated_params * 2 if estimated_params else 0
        estimated_size_mb = estimated_size_gb * 1024
        
        return {
            "size_bytes": int(estimated_size_mb * 1024 * 1024),
            "size_mb": estimated_size_mb,
            "size_gb": estimated_size_gb,
            "parameter_count": f"~{estimated_params}B" if estimated_params else "Unknown",
            "quantization": "Estimated"
        }
    
    def measure_load_time(self, model_name: str) -> float:
        """Measure how long it takes to load a model"""
        start_time = time.time()
        
        try:
            # Send a minimal request to trigger model loading
            response = requests.post(
                f"http://localhost:11434/api/generate",
                json={"model": model_name, "prompt": "Hi", "stream": False},
                timeout=120
            )
            
            end_time = time.time()
            
            if response.status_code == 200:
                return end_time - start_time
            else:
                print(f"Failed to load model {model_name}: {response.status_code}")
                return -1
                
        except Exception as e:
            print(f"Error measuring load time for {model_name}: {e}")
            return -1

class TokenCounter:
    def __init__(self):
        self.tokenizers = {}
    
    def get_tiktoken_count(self, text: str, model: str = "gpt-3.5-turbo") -> int:
        """Count tokens using tiktoken (OpenAI's tokenizer)"""
        try:
            encoding = tiktoken.encoding_for_model(model)
            return len(encoding.encode(text))
        except:
            # Fallback to cl100k_base encoding
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
    
    def get_hf_tokenizer_count(self, text: str, model_name: str) -> int:
        """Count tokens using HuggingFace tokenizer"""
        try:
            if model_name not in self.tokenizers:
                self.tokenizers[model_name] = AutoTokenizer.from_pretrained(
                    model_name, 
                    trust_remote_code=True
                )
            tokenizer = self.tokenizers[model_name]
            return len(tokenizer.encode(text))
        except Exception as e:
            print(f"Could not load tokenizer for {model_name}: {e}")
            return self._fallback_count(text)
    
    def _fallback_count(self, text: str) -> int:
        """Fallback token counting (words + punctuation)"""
        import re
        # More accurate than char/4 - counts words and punctuation separately
        words = len(re.findall(r'\w+', text))
        punctuation = len(re.findall(r'[^\w\s]', text))
        return words + punctuation


class ModelBenchmark:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.token_counter = TokenCounter()
        self.system_monitor = SystemMonitor()
        
        # Model-specific tokenizer mappings
        self.model_tokenizer_map = {
            "llama2": "meta-llama/Llama-2-7b-hf",
            "llama3": "meta-llama/Meta-Llama-3-8B",
            "llama3.2": "meta-llama/Llama-3.2-3B",
            "mistral": "mistralai/Mistral-7B-v0.1",
            "codellama": "codellama/CodeLlama-7b-Python-hf",
            "phi": "microsoft/phi-2",
            "phi3": "microsoft/Phi-3-mini-4k-instruct",
            "gemma": "google/gemma-7b",
            "qwen": "Qwen/Qwen-7B",
            "qwen2.5": "Qwen/Qwen2.5-7B",
            "deepseek": "deepseek-ai/deepseek-coder-6.7b-base",
            "smollm2": "HuggingFaceTB/SmolLM2-1.7B",
        }
        
        self.models = {
            "smollm2:1.7b": "smollm2:1.7b",
            "deepseek-r1:1.5b": "deepseek-r1:1.5b", 
            "phi3:mini": "phi3:mini",  
            "gemma:2b": "gemma:2b",
            "llama3.2": "llama3.2",
            "qwen2.5:3b": "qwen2.5:3b",
        }
    
    def count_tokens(self, text: str, model_name: str) -> int:
        """Count tokens using the most appropriate method for the model"""
        model_base = model_name.split(':')[0].lower()
        
        # Try HuggingFace tokenizer first
        if model_base in self.model_tokenizer_map:
            hf_model = self.model_tokenizer_map[model_base]
            return self.token_counter.get_hf_tokenizer_count(text, hf_model)
        
        # Fallback to tiktoken for general use
        return self.token_counter.get_tiktoken_count(text)
    
    def _save_response_to_file(self, model_name: str, response: str) -> None:
        """Save the model response to a file in the benchmarks directory"""
        try:
            # Ensure benchmarks directory exists
            benchmarks_dir = "./benchmarks"
            os.makedirs(benchmarks_dir, exist_ok=True)
            
            # Generate timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Clean model name for filename (replace special characters)
            clean_model_name = model_name.replace(":", "-").replace("/", "-")
            
            # Create filename
            filename = f"response-{clean_model_name}-{timestamp}.txt"
            filepath = os.path.join(benchmarks_dir, filename)
            
            # Save response to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Model: {model_name}\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                f.write("="*50 + "\n\n")
                f.write(response)
                
            print(f"Response saved to: {filepath}")
            
        except Exception as e:
            print(f"Error saving response to file: {e}")
    
    def benchmark_with_streaming(self, model_name: str, prompt: str) -> Dict:
        """Benchmark with streaming and accurate token counting"""
        print(f"Benchmarking {model_name} with streaming...")
        
        # Start system monitoring
        self.system_monitor.start_monitoring()
        
        start_time = time.time()
        response_chunks = []
        chunk_times = []
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model_name,
                    "prompt": prompt,
                    "stream": True
                },
                stream=True,
                timeout=300  # 5 minute timeout
            )
            
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        if "response" in data and data["response"]:
                            response_chunks.append(data["response"])
                            chunk_times.append(time.time())
                        if data.get("done", False):
                            break
                    except json.JSONDecodeError:
                        continue
            
            end_time = time.time()
            full_response = "".join(response_chunks)
            
            # Stop system monitoring and get metrics
            system_metrics = self.system_monitor.stop_monitoring()
            
            # Save response to file
            self._save_response_to_file(model_name, full_response)
            
            # Count tokens accurately
            prompt_tokens = self.count_tokens(prompt, model_name)
            response_tokens = self.count_tokens(full_response, model_name)
            total_tokens = prompt_tokens + response_tokens
            
            total_duration = end_time - start_time
            
            # Calculate time to first token
            time_to_first_token = chunk_times[0] - start_time if chunk_times else 0
            
            # Calculate streaming metrics
            if len(chunk_times) > 1:
                streaming_duration = chunk_times[-1] - chunk_times[0]
                streaming_tokens_per_sec = response_tokens / streaming_duration if streaming_duration > 0 else 0
            else:
                streaming_tokens_per_sec = 0
            
            # Get model size information
            model_size_info = self.system_monitor.get_model_size(model_name)
            
            return {
                "model": model_name,
                "prompt_tokens": prompt_tokens,
                "response_tokens": response_tokens,
                "total_tokens": total_tokens,
                "total_duration": total_duration,
                "time_to_first_token": time_to_first_token,
                "overall_tokens_per_second": total_tokens / total_duration if total_duration > 0 else 0,
                "response_tokens_per_second": response_tokens / total_duration if total_duration > 0 else 0,
                "streaming_tokens_per_second": streaming_tokens_per_sec,
                "chunks_received": len(response_chunks),
                "response_length_chars": len(full_response),
                
                # New system metrics
                "peak_memory_mb": system_metrics["peak_memory_mb"],
                "avg_cpu_percent": system_metrics["avg_cpu_percent"],
                "max_cpu_percent": system_metrics["max_cpu_percent"],
                "avg_gpu_utilization": system_metrics["avg_gpu_utilization"],
                "max_gpu_utilization": system_metrics["max_gpu_utilization"],
                
                # Model information
                "model_size_mb": model_size_info["size_mb"],
                "model_size_gb": model_size_info["size_gb"],
                "parameter_count": model_size_info["parameter_count"],
                "quantization": model_size_info["quantization"],
                
                # Quality metrics (placeholder)
                "response_quality_score": "TBC",
                "relevance_score": "TBC",
                
                "success": True
            }
            
        except Exception as e:
            # Stop monitoring in case of error
            self.system_monitor.stop_monitoring()
            return {"model": model_name, "error": str(e), "success": False}
    
    def benchmark_single_query(self, model_name: str, prompt: str, runs: int = 3) -> Dict:
        """Benchmark a single model with multiple runs using proper token counting"""
        results = []
        
        # Measure load time for the model (only once)
        print(f"  Measuring load time for {model_name}...")
        load_time = self.system_monitor.measure_load_time(model_name)
        
        for run in range(runs):
            print(f"  Run {run + 1}/{runs} for {model_name}")
            result = self.benchmark_with_streaming(model_name, prompt)
            if result.get("success", False):
                results.append(result)
            else:
                print(f"  ✗ Run {run + 1} failed: {result.get('error', 'Unknown error')}")
        
        if not results:
            return {"model": model_name, "error": "All runs failed", "success": False}
        
        # Calculate averages
        avg_result = {
            "model": model_name,
            "runs_completed": len(results),
            "runs_attempted": runs,
            "success_rate": len(results) / runs,
            "load_time_seconds": load_time,
            "avg_prompt_tokens": sum(r["prompt_tokens"] for r in results) / len(results),
            "avg_response_tokens": sum(r["response_tokens"] for r in results) / len(results),
            "avg_total_tokens": sum(r["total_tokens"] for r in results) / len(results),
            "avg_total_duration": sum(r["total_duration"] for r in results) / len(results),
            "avg_time_to_first_token": sum(r["time_to_first_token"] for r in results) / len(results),
            "avg_overall_tokens_per_second": sum(r["overall_tokens_per_second"] for r in results) / len(results),
            "avg_response_tokens_per_second": sum(r["response_tokens_per_second"] for r in results) / len(results),
            "avg_streaming_tokens_per_second": sum(r["streaming_tokens_per_second"] for r in results) / len(results),
            "min_tokens_per_second": min(r["response_tokens_per_second"] for r in results),
            "max_tokens_per_second": max(r["response_tokens_per_second"] for r in results),
            "std_tokens_per_second": statistics.stdev([r["response_tokens_per_second"] for r in results]) if len(results) > 1 else 0,
            
            # System metrics averages
            "avg_peak_memory_mb": sum(r["peak_memory_mb"] for r in results) / len(results),
            "max_peak_memory_mb": max(r["peak_memory_mb"] for r in results),
            "avg_cpu_percent": sum(r["avg_cpu_percent"] for r in results) / len(results),
            "max_cpu_percent": max(r["max_cpu_percent"] for r in results),
            "avg_gpu_utilization": sum(r["avg_gpu_utilization"] for r in results) / len(results),
            "max_gpu_utilization": max(r["max_gpu_utilization"] for r in results),
            
            # Model info (same for all runs)
            "model_size_mb": results[0]["model_size_mb"] if results else 0,
            "model_size_gb": results[0]["model_size_gb"] if results else 0,
            "parameter_count": results[0]["parameter_count"] if results else "Unknown",
            "quantization": results[0]["quantization"] if results else "Unknown",
            
            # Quality scores (placeholder)
            "response_quality_score": "TBC",
            "relevance_score": "TBC",
            
            "individual_results": results
        }
        
        return avg_result
    
    def run_benchmark(self, test_prompts: List[str], runs_per_prompt: int = 3):
        """Run benchmark across all models and prompts with token counting"""
        results = {}
        
        for model_name in self.models.keys():
            print(f"\n{'='*50}")
            print(f"Benchmarking {model_name}...")
            print('='*50)
            model_results = {}
            
            for i, prompt in enumerate(test_prompts):
                print(f"\nPrompt {i+1}/{len(test_prompts)}: {prompt[:50]}...")
                prompt_results = self.benchmark_single_query(model_name, prompt, runs_per_prompt)
                model_results[f"prompt_{i+1}"] = prompt_results
                
                if prompt_results.get("success_rate", 0) > 0:
                    print(f"  ✓ Avg tokens/sec: {prompt_results['avg_response_tokens_per_second']:.2f}")
                    print(f"  ✓ Time to first token: {prompt_results['avg_time_to_first_token']:.3f}s")
                    print(f"  ✓ Peak memory: {prompt_results['avg_peak_memory_mb']:.1f} MB")
                    print(f"  ✓ Load time: {prompt_results['load_time_seconds']:.2f}s")
                else:
                    print(f"  ✗ All runs failed")
                
            results[model_name] = model_results
        
        return results
    
    def generate_report(self, results: Dict) -> str:
        """Generate a formatted benchmark report with enhanced metrics"""
        report = "# Enhanced Model Benchmark Report\n\n"
        
        # Summary table with new metrics
        report += "## Summary\n\n"
        report += "| Model | Tokens/sec | TTFT (s) | Memory (MB) | CPU % | GPU % | Size (GB) | Load Time (s) | Quality | Relevance |\n"
        report += "|-------|------------|----------|-------------|-------|-------|-----------|---------------|---------|-----------|\\n"
        
        for model_name, model_results in results.items():
            all_tokens_per_sec = []
            all_ttft = []
            all_memory = []
            all_cpu = []
            all_gpu = []
            all_load_time = []
            total_success = 0
            total_attempts = 0
            model_size_gb = 0
            
            for prompt_result in model_results.values():
                if prompt_result.get("success_rate", 0) > 0:
                    all_tokens_per_sec.append(prompt_result["avg_response_tokens_per_second"])
                    all_ttft.append(prompt_result["avg_time_to_first_token"])
                    all_memory.append(prompt_result["avg_peak_memory_mb"])
                    all_cpu.append(prompt_result["avg_cpu_percent"])
                    all_gpu.append(prompt_result["avg_gpu_utilization"])
                    all_load_time.append(prompt_result["load_time_seconds"])
                    total_success += prompt_result["runs_completed"]
                    total_attempts += prompt_result["runs_attempted"]
                    model_size_gb = prompt_result["model_size_gb"]
            
            avg_tokens_per_sec = statistics.mean(all_tokens_per_sec) if all_tokens_per_sec else 0
            avg_ttft = statistics.mean(all_ttft) if all_ttft else 0
            avg_memory = statistics.mean(all_memory) if all_memory else 0
            avg_cpu = statistics.mean(all_cpu) if all_cpu else 0
            avg_gpu = statistics.mean(all_gpu) if all_gpu else 0
            avg_load_time = statistics.mean(all_load_time) if all_load_time else 0
            
            report += f"| {model_name} | {avg_tokens_per_sec:.2f} | {avg_ttft:.3f} | {avg_memory:.1f} | {avg_cpu:.1f} | {avg_gpu:.1f} | {model_size_gb:.2f} | {avg_load_time:.2f} | TBC | TBC |\n"
        
        # Detailed results
        report += "\n## Detailed Results\n\n"
        for model_name, model_results in results.items():
            report += f"### {model_name}\n\n"
            for prompt_name, prompt_result in model_results.items():
                if prompt_result.get("success_rate", 0) > 0:
                    report += f"**{prompt_name}:**\n"
                    report += f"- Response Tokens/sec: {prompt_result['avg_response_tokens_per_second']:.2f}\n"
                    report += f"- Time to First Token: {prompt_result['avg_time_to_first_token']:.3f}s\n"
                    report += f"- Peak Memory Usage: {prompt_result['avg_peak_memory_mb']:.1f} MB\n"
                    report += f"- Average CPU Usage: {prompt_result['avg_cpu_percent']:.1f}%\n"
                    report += f"- Average GPU Usage: {prompt_result['avg_gpu_utilization']:.1f}%\n"
                    report += f"- Model Size: {prompt_result['model_size_gb']:.2f} GB\n"
                    report += f"- Load Time: {prompt_result['load_time_seconds']:.2f}s\n"
                    report += f"- Parameter Count: {prompt_result['parameter_count']}\n"
                    report += f"- Response Quality: {prompt_result['response_quality_score']}\n"
                    report += f"- Relevance Score: {prompt_result['relevance_score']}\n"
                    report += f"- Success Rate: {prompt_result['success_rate']:.1%}\n\n"
                else:
                    report += f"**{prompt_name}:** Failed - {prompt_result.get('error', 'Unknown error')}\n\n"
        
        return report
    
    def print_summary(self, results: Dict):
        """Print a comprehensive summary with enhanced metrics"""
        print("\n" + "="*100)
        print("ENHANCED MODEL BENCHMARK RESULTS")
        print("="*100)
        
        # Collect model performance data
        model_performance = []
        
        for model_name, model_results in results.items():
            all_tokens_per_sec = []
            all_ttft = []
            all_memory = []
            all_cpu = []
            all_gpu = []
            all_load_time = []
            total_success = 0
            total_attempts = 0
            model_size_gb = 0
            
            for prompt_result in model_results.values():
                if prompt_result.get("success_rate", 0) > 0:
                    all_tokens_per_sec.append(prompt_result["avg_response_tokens_per_second"])
                    all_ttft.append(prompt_result["avg_time_to_first_token"])
                    all_memory.append(prompt_result["avg_peak_memory_mb"])
                    all_cpu.append(prompt_result["avg_cpu_percent"])
                    all_gpu.append(prompt_result["avg_gpu_utilization"])
                    all_load_time.append(prompt_result["load_time_seconds"])
                    total_success += prompt_result["runs_completed"]
                    total_attempts += prompt_result["runs_attempted"]
                    model_size_gb = prompt_result["model_size_gb"]
            
            if all_tokens_per_sec:
                model_performance.append({
                    "model": model_name,
                    "avg_tokens_per_sec": statistics.mean(all_tokens_per_sec),
                    "avg_ttft": statistics.mean(all_ttft),
                    "avg_memory": statistics.mean(all_memory),
                    "avg_cpu": statistics.mean(all_cpu),
                    "avg_gpu": statistics.mean(all_gpu),
                    "avg_load_time": statistics.mean(all_load_time),
                    "model_size_gb": model_size_gb,
                    "success_rate": total_success / total_attempts
                })
        
        # Sort by tokens per second
        model_performance.sort(key=lambda x: x["avg_tokens_per_sec"], reverse=True)
        
        for rank, data in enumerate(model_performance, 1):
            print(f"\n{rank}. {data['model']}")
            print(f"   Tokens/sec: {data['avg_tokens_per_sec']:.2f}")
            print(f"   Time to first token: {data['avg_ttft']:.3f}s")
            print(f"   Peak memory: {data['avg_memory']:.1f} MB")
            print(f"   CPU usage: {data['avg_cpu']:.1f}%")
            print(f"   GPU usage: {data['avg_gpu']:.1f}%")
            print(f"   Model size: {data['model_size_gb']:.2f} GB")
            print(f"   Load time: {data['avg_load_time']:.2f}s")
            print(f"   Success rate: {data['success_rate']:.1%}")
        
        if not model_performance:
            print("\nNo successful benchmark results to display.")
        
        print("\n" + "="*100)


# Test prompts of varying complexity
test_prompts = [
    """You are a professional content creator writing engaging executive summaries for a general audience.

Transform the following {text} into a compelling, conversational podcast that tells the story of the topic. 

Requirements:
- Start directly with the main topic - no meta-commentary about the task
- Write in a natural, storytelling tone as if explaining to a friend
- Focus on the key insights and practical applications
- Make complex concepts accessible without oversimplifying
- Structure the content to flow logically from introduction to conclusion
- Keep the audience engaged throughout
- Your summary is for a podcast
- Your summary must be in a single paragraph
- Your summary must be shorter than 500 words
- Skip all the links (http, https, www) and references in the text
- Skip "thinking" (<think>) in reasoning models (deepseek), and only return the final answer

The structure of your reponses look like 

Part 1: Introduction (a single paragraph)
Part 2: Key Takeaways  (a single paragraph)
Part 3: Recommendations  (a single paragraph)
Part 4: Conclusions  (a single paragraph)

{text}
## Table of Contents  
1. Executive Summary  
2. Introduction  
3. Defining Cross-selling and Upselling in Modern Business  
4. Challenges in Cross-selling and Upselling  
5. Data Mining: Concepts, Techniques, and Benefits  
6. Data Mining Applications in Cross-selling and Upselling  
7. Case Studies of Successful Data Mining Applications  
 7.1 IT/ITES Industry: Enhancing Internal Collaboration and Sales Efficiency  
 7.2 Banking Sector: Increasing Conversion through Data-Driven Behavioral Insights  
 7.3 Telecom Industry: Transformative Analytics for Cross-selling Quad-Play Services  
 7.4 Retail and E-commerce: Leveraging Personalization and Dynamic Recommendations  
8. Implementation Best Practices for Data Mining in Sales Optimization  
9. Conclusions and Future Trends  
10. References and Acknowledgments  

---  

## 1. Executive Summary  

In today's hyper-competitive business environment, effective cross-selling and upselling are critical levers to increase revenue, improve customer lifetime value, and bolster competitive differentiation. This report provides a comprehensive analysis of successful data mining applications that have enhanced cross-selling and upselling strategies across industries. Drawing on detailed case studies from IT/ITES organizations, global banks, telecommunications firms, and retail e-commerce brands, the report discusses the inherent challenges in traditional sales processes and demonstrates how advanced data mining techniques—such as clustering, regression, classification, and association rule learning—can illuminate hidden insights and drive actionable business outcomes.  

Key findings include the establishment of robust frameworks to overcome internal silos, the development of improved client-centric case studies, and transformative technology deployments that have led to notable performance improvements. For instance, in the telecommunications industry, the deployment of a proprietary Customer Intelligence solution resulted in the doubling of cross-selling efforts and a significant reduction in order cancellations. Similarly, a global bank leveraged data analytics and behavioral science to boost conversion rates by 50%. Furthermore, the integration of personalized product recommendation strategies in e-commerce has consistently driven improvements in average order value and customer retention.  

This report not only synthesizes key industry insights but also maps out a structured strategy for the application of data mining in driving effective cross-selling and upselling. By detailing best practices, technological enablers, and future trends, it offers insights for sales and marketing managers, data scientists, and business intelligence professionals aiming to harness the power of data to optimize customer engagement strategies.  

---  

## 2. Introduction  

In today's dynamic marketplace, companies face increasing pressure to maximize revenue from existing clients. Cross-selling and upselling are two sales tactics employed to deepen customer relationships and boost profitability. Cross-selling involves recommending complementary products or services that enhance a customer's overall experience, whereas upselling encourages customers to purchase higher-end products or additional features on top of their current selection. With rapid developments in artificial intelligence (AI), machine learning (ML), and big data analytics, data mining has emerged as a pivotal technology to enhance these strategies.  

The significance of data mining lies in its ability to process large volumes of heterogeneous data, extract actionable insights, and enable business leaders to make data-driven decisions. This report delves into how these advanced techniques are applied to improve cross-selling and upselling efforts. We explore successful implementations across multiple sectors and discuss how data mining not only uncovers hidden opportunities but also mitigates challenges such as internal silos, data quality issues, and ineffective sales narratives.  

As organizations move towards more strategic and proactive sales approaches, the integration of data mining in cross-selling and upselling has proven essential for competitive advantage. This report, supported by extensive case studies and empirical data, provides a step-by-step analysis of the methods and best practices that drive revenue growth through optimized sales processes.  

---  

## 3. Defining Cross-selling and Upselling in Modern Business  

Cross-selling and upselling are fundamental approaches in sales strategy designed to enhance customer value and generate incremental revenue. Although both tactics aim to increase sales, they differ in their focus and application:  

- **Cross-selling**: This strategy involves recommending additional products or services that complement the items a customer is already considering. The goal is to provide enhanced value by addressing a broader set of customer needs without fundamentally altering the original purchase decision. For example, recommending a phone case or accessories when a customer purchases a smartphone is a quintessential example of cross-selling.  

- **Upselling**: Upselling, on the other hand, incentives customers to opt for a more premium version of a product or to buy additional features that enhance the base product. This tactic is designed to increase the overall sale value by shifting customer choice toward higher-margin products. For instance, encouraging a customer to upgrade to a latest model or to add extended warranty on an electronic device represents typical upselling.  

Both tactics are intrinsically linked to customer behavior and require a deep understanding of customer preferences and purchase histories. Data mining empowers businesses to analyze vast datasets to detect buying patterns, correlate product affinities, and ultimately tailor recommendations to maximize opportunities. These methods are especially critical in sectors where sales processes are complex or where multiple product categories are involved, such as IT/ITES, banking, telecom, and retail.  

---  

## 4. Challenges in Cross-selling and Upselling  

While cross-selling and upselling offer substantial benefits in boosting customer lifetime value (CLTV) and generating sustainable revenue, several challenges complicate their execution. Traditional sales initiatives often struggle with issues such as communication silos, data fragmentation, and suboptimal messaging. The primary challenges identified across various sectors include:  

### 4.1 Internal Silos and Limited Knowledge Sharing  

Large organizations, particularly in IT and ITES sectors, frequently encounter knowledge silos. Different departments or geographical regions often operate in isolation, leading to missed opportunities to share success stories or leverage proven case studies in sales efforts. When teams are unaware of innovations or successful sales initiatives from other regions, they are less likely to replicate these achievements in cross-selling and upselling scenarios.  

### 4.2 Complex Product Messaging and Client Confidentiality  

Case studies and sales narratives frequently suffer from overemphasis on technical details and inadequate focus on addressing client pain points. The technical jargon used in successful projects may not resonate with prospective clients who are more concerned with business outcomes. Additionally, stringent client confidentiality rules necessitate the omission of certain critical details from case studies, hindering the development of persuasive sales collateral.  

### 4.3 Outdated Sales Materials  

Another significant challenge is the reliance on outdated case studies that do not accurately reflect current market dynamics or emerging customer needs. Sales teams often struggle with materials that are not regularly updated, which reduces their efficacy during pre-sales activities and in responding to high-value RFPs.  

### 4.4 Data Quality and Integration Issues  

Data mining itself faces challenges such as data quality issues, integration obstacles, and handling the vast volume of data available today. Inaccurate or incomplete data can lead to misleading insights, while disparate data sources require effective integration strategies to ensure that insights are both accurate and actionable.  

### 4.5 Process Complexity and Bureaucracy  

The process of creating and approving case studies or sales materials can be overly bureaucratic, leading to significant delays. Multiple stakeholders and lengthy approval processes often result in missed opportunities where timely action could have leveraged market momentum.  

The following table summarizes the main challenges in cross-selling and upselling:  

| **Challenge**                         | **Description**                                                                                                                                                                    | **Impacted Area**                   |  
|---------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------|  
| Internal Silos                        | Lack of visibility into success stories across regions due to departmental and geographical isolation                                                                               | Sales and Knowledge Sharing         |  
| Complex Messaging & Client Confidentiality | Overemphasis on technical details and omission of crucial client benefits due to confidentiality agreements                                                                            | Sales Collateral & Messaging        |  
| Outdated Materials                    | Use of old case studies and collateral that do not address current market needs                                                                                                     | Pre-sales Efficiency                |  
| Data Quality and Integration          | Inaccurate, incomplete, or fragmented data leading to misleading insights                                                                                                           | Data Analytics and Decision-making  |  
| Process Complexity                    | Bureaucratic procedures that delay the creation and deployment of effective sales materials                                                                                         | Operational Efficiency              |  

Each of these challenges calls for innovative solutions that leverage robust data mining techniques to extract actionable insights and optimize the approach to sales.  

---  

## 5. Data Mining: Concepts, Techniques, and Benefits  

Data mining is the process of extracting meaningful patterns and insights from vast amounts of data by utilizing statistical, computational, and machine learning techniques. In the realm of cross-selling and upselling, data mining serves as a critical tool for uncovering patterns of consumer behavior, predicting future trends, and personalizing customer interactions.  

### 5.1 Fundamental Data Mining Process  

The core data mining process involves several key steps:  

1. **Goal Analysis**: Defining the objectives of the data mining project is essential. Business analysts and data scientists collaborate to determine the specific problems to solve or the opportunities to exploit.  
2. **Data Selection**: This involves identifying relevant data sources, such as customer databases, transaction logs, or CRM systems, that will feed into the analysis.  
3. **Data Cleaning and Transformation**: Raw data often contains noise or inconsistencies. Cleaning the data ensures accuracy, while transformation standardizes the data for seamless analysis.  
4. **Model Building**: Various statistical and machine-learning techniques are applied to build models that can detect patterns or predict outcomes. Techniques such as classification, regression, and clustering are commonly used.  
5. **Analysis and Interpretation**: Once models are built, the data is analyzed and interpreted. The results are then visualized to support informed decision-making and strategic planning.  

### 5.2 Key Data Mining Techniques for Cross-selling and Upselling  

Data mining techniques that are particularly useful for enhancing cross-selling and upselling initiatives include:  

- **Association Rule Learning**: This technique identifies items that frequently occur together, thereby uncovering product affinities and complementary purchases. For example, analysis might reveal that customers who buy a smartphone are highly likely to purchase a protective case.  
- **Clustering**: Clustering algorithms group customers into segments based on their behavior or demographics. This segmentation enables personalized marketing efforts and tailored cross-sell recommendations.  
- **Regression Analysis**: Regression models help quantify the relationship between different variables, such as marketing spend and sales conversion rates. This analytical approach is critical in forecasting and scenario planning.  
- **Classification**: Classification algorithms assign customers to predefined categories based on historical behavior. This can be used to predict customer response to upsell offers or determine susceptibility to cross-sell recommendations.  
- **Decision Trees**: Decision trees break down complex decision-making into simple, interpretable rules. This contributes to a transparent sales strategy that can be easily communicated throughout the organization.  

The following table compares major data mining techniques with their applications and benefits in sales strategies:  

| **Data Mining Technique**   | **Application in Sales**                                          | **Primary Benefit**                                               |  
|-----------------------------|-------------------------------------------------------------------|-------------------------------------------------------------------|  
| Association Rule Learning   | Identifying complementary product pairs                           | Enhanced product bundling and increased average order value       |  
| Clustering                  | Segmentation based on customer behavior                           | Personalized targeting and improved campaign relevance            |  
| Regression Analysis         | Forecasting sales trends and relationships                        | Optimized budget allocation and performance prediction             |  
| Classification              | Predicting customer responsiveness                                 | Automated decision-making and targeted upsell strategies            |  
| Decision Trees              | Simplifying complex decision paths in the sales process           | Transparent, interpretable sales strategies and improved training   |  

### 5.3 Benefits of Data Mining in Sales Optimization  

The application of data mining in cross-selling and upselling leads to numerous benefits:  
- **Actionable Insights**: Data mining simplifies vast amounts of data into actionable insights that directly inform sales strategies.  
- **Enhanced Personalization**: By segmenting customers effectively, companies can tailor product recommendations that are highly relevant to individual needs.  
- **Improved Forecast Accuracy**: Advanced predictive analytics enable more accurate forecasts of customer behavior and sales trends, making it easier to plan marketing campaigns and inventory management.  
- **Operational Efficiency**: Streamlining complex datasets results in efficient allocation of resources and faster decision-making cycles in sales processes.  
- **Revenue Growth**: With better targeted sales efforts, companies can realize significant improvements in conversion rates and overall revenue.  

In summary, data mining not only identifies hidden opportunities but also bridges the gap between complex technical solutions and customer-centric sales pitches, ensuring that strategies are both effective and adaptable.  

---  

## 6. Data Mining Applications in Cross-selling and Upselling  

Data mining has successfully transformed traditional sales approaches, enabling organizations to move from reactive selling to proactive and dynamic customer engagement strategies. This transformation is evident across multiple industries where data mining techniques have been integrated into daily sales operations to re-engineer case studies, empower sales teams, and personalize marketing efforts.  

### 6.1 Overcoming Sales Challenges with Data Mining  

Leveraging data mining allows companies to:  
- **Break Down Internal Silos**: By aggregating data from across regions and departments, organizations can overcome geographical or departmental isolation and share best practices more effectively.  
- **Refine Customer Messaging**: Advanced analytics help to distill technical details into compelling business cases that are understandable and relatable for customers.  
- **Update Sales Collateral in Real-time**: Data-driven insights ensure that case studies and other sales materials remain current and dynamically update to reflect new market trends and customer needs.  
- **Mitigate Data Quality Issues**: Advanced cleaning and transformation techniques ensure that sales teams rely on accurate, high-quality data for their decision-making processes.  

### 6.2 How Data Mining Drives Effective Cross-selling and Upselling  

Data mining provides the tools to pinpoint opportunities that might otherwise be overlooked. For example:  
- **Customer Behavior Analysis**: By mapping customer purchase histories, data mining can highlight patterns that reveal latent needs and preferences. This is particularly useful for identifying new cross-sell opportunities within segments that are already engaged with the brand.  
- **Predictive Modeling**: Predictive algorithms forecast which customers are more likely to respond to upsell offers, allowing sales teams to prioritize leads and focus their efforts effectively.  
- **Real-time Analytics**: Integration of real-time data feeds ensures that sales teams can quickly adapt to shifting market conditions or customer sentiments, facilitating timely adjustments in sales strategies.  
- **Enhanced Personalization**: With customer segmentation based on historical and demographic data, recommendations are tailored to suit the specific needs of each customer, thereby increasing the likelihood of conversion.  

The following mermaid diagram outlines a typical process flow for implementing data mining in cross-selling and upselling initiatives:  

```mermaid  
flowchart TD  
  A["Define Business Objective"] --> B["Collect Customer Data"]  
  B --> C["Clean and Transform Data"]  
  C --> D["Apply Data Mining Techniques"]  
  D --> E["Generate Predictive Models"]  
  E --> F["Segment Customers Based on Insights"]  
  F --> G["Develop Personalized Sales Recommendations"]  
  G --> H["Deploy Targeted Sales Campaigns"]  
  H --> I["Monitor Campaign Performance"]  
  I --> END[END]  
```  

**Figure: Process Flow for Leveraging Data Mining in Cross-selling and Upselling Initiatives**  
This diagram illustrates the sequential process starting from defining clear business objectives to continuously monitoring the performance of targeted campaigns, making it evident how data mining integrates into the sales workflow to drive actionable business outcomes.  

### 6.3 Integration with Business Intelligence Systems  

Modern Business Intelligence (BI) platforms integrate seamlessly with data mining tools, creating a unified ecosystem that continuously informs sales strategies:  
- **AI-Powered Analytics**: Trends such as the embedding of AI within BI systems ensure that data mining results are actionable in real time. Organizations increasingly rely on platforms that offer integrated analytics, dashboards, and predictive models to improve decision-making.  
- **Real-time Data Integration**: The ability to ingest and process data from various sources in real time empowers businesses to quickly adapt to market changes, a critical capability in rapidly evolving sectors like retail and telecom.  
- **User-Friendly Visualizations**: Advanced BI tools convert complex data mining outputs into intuitive visualizations—graphs, charts, and tables—that support a broad range of business users, from top executives to front-line sales teams.  

---  

## 7. Case Studies of Successful Data Mining Applications  

Successful real-world case studies demonstrate the tangible benefits of integrating data mining with cross-selling and upselling strategies. The following sections detail key implementations in various industries, illustrating the methodological approach, implementation best practices, and achieved results.  

### 7.1 IT/ITES Industry: Enhancing Internal Collaboration and Sales Efficiency  

Large IT and ITES organizations, often with employee counts exceeding 50,000, face inherent challenges due to internal silos and fragmented communication channels. Sales teams traditionally miss opportunities for cross-selling and upselling because they lack visibility into the successful initiatives in other regions or verticals.  

**Key Implementation Strategies:**  
- **Understanding the Business Context:** Consulting engagements have shown that gaining a comprehensive understanding of both manufacturing and IT/ITES landscapes is critical. This includes engaging stakeholders across departments to identify unique sales opportunities.  
- **Harnessing Design Thinking:** Using design thinking frameworks and mind mapping tools to craft well-organized case studies that focus on solving customer pain points has been a core strategy.  
- **Multi-format Delivery:** Case studies were produced in both PDF and slide formats to ensure that they are easily accessible during client meetings and RFP responses.  

**Results:**  
The tailored approach resulted in:  
- Enhanced pre-sales efficiency across regions  
- Proactive sales pitching leading to alterations in strategy and revenue potential  
- A potential forecasted sales increase of around 10%  

These case studies highlight the importance of leveraging data mining insights to break down silos and deliver tailored, up-to-date, and business-oriented sales narratives that resonate with clients.  

---  

### 7.2 Banking Sector: Increasing Conversion through Data-Driven Behavioral Insights  

A leading global bank faced declining cross-selling performance for high-value financial products in a post-pandemic environment. To address this, the bank collaborated with external consultants to integrate data mining with behavioral science methodologies.  

**Key Implementation Strategies:**  
- **Leveraging Data Analytics and Behavioral Science:** The bank utilized advanced analytics to identify psychological barriers and refine its sales process. The solution incorporated comprehensive sales audits alongside the deployment of digital tools and optimized scripts for the sales team.  
- **Optimization of Sales Scripts:** By integrating data-driven insights into sales communications, the bank was able to craft targeted messaging that better addressed customer pain points.  
- **Empowering Sales Teams through Training:** Ongoing training focused on improving objection handling and refining sales pitches was implemented based on insights derived from data analytics.  

**Results:**  
- A marked 50% increase in conversion rates for cross-selling initiatives was recorded.  
- The bank experienced noticeable improvements in how sales teams engaged prospects by aligning technical capabilities with business benefits.  

This case study exemplifies the use of data mining to transform traditional sales processes into dynamic, behavior-driven practices that significantly enhance conversion rates and customer acquisition outcomes.  

---  

### 7.3 Telecom Industry: Transformative Analytics for Cross-Selling Quad-Play Services  

A major US telecom conglomerate, with over 28 million subscribers, embarked on an ambitious project to improve cross-selling across its quadruple-play services (voice, broadband, TV, and mobile). Prior to intervention, only 9% of non-sales interactions resulted in cross-selling opportunities.  

**Key Implementation Strategies:**  
- **Deployment of Proprietary Customer Intelligence Software:** Firstsource introduced the firstCustomer Intelligence (FCI) solution to analyze customer interactions using speech, text, and competitor analysis.  
- **Identification of Sales Opportunities:** Data analysis revealed that associates had opportunities to pitch cross-selling offers on 22% of non-sales interactions. However, issues such as lengthy switching processes, customer satisfaction with current packages, and processing errors were identified as major obstacles.  
- **Recommendations and Process Improvements:** Through detailed analytics, Firstsource recommended improvements in sales pitch quality, better objection handling, stringent adherence to compliance, and streamlining the order processing workflow. These recommendations led to a 110% potential improvement in associate performance.  

**Results:**  
- Cross-selling performance doubled, with the pitch rate increasing from 9% to over 20%.  
- Order cancellation rates were reduced to below 5% as a direct result of process improvements.  

The telecom case study underscores the transformative power of data mining in identifying latent opportunities and driving process enhancements in highly complex sales environments.  

---  

### 7.4 Retail and E-commerce: Leveraging Personalization and Dynamic Recommendations  

Retailers and e-commerce platforms use data mining extensively to personalize customer experiences and optimize average order values (AOV). Multiple cases from industry leaders illustrate the significance of tailored cross-selling and upselling strategies.  

**Key Implementation Strategies:**  
- **Personalized Recommendations:** Retailers deploy association rule learning and clustering techniques to analyze customer purchase histories and behavioral patterns. For instance, the "Frequently Bought Together" feature seen on platforms like Amazon is a direct outcome of such data mining efforts.  
- **Enhanced User Experience through Post-Purchase Upsells:** E-commerce brands, such as those using Aftersell's tools, have significantly boosted their AOV by implementing dynamic, personalized post-purchase recommendations.  
- **Tracking Campaign Performance:** Continuous monitoring and A/B testing of cross-sell and upsell campaigns ensure that recommendations remain relevant and effective. This dynamic approach results in sustained improvements in customer engagement and revenue growth.  

The following table highlights key performance metrics observed in retail and e-commerce implementations of data mining for cross-selling and upselling:  

| **Metric**                     | **Result/Impact**                                       | **Source Reference**          |  
|--------------------------------|---------------------------------------------------------|-------------------------------|  
| Increase in Average Order Value (AOV) | Notable incremental gains observed (e.g., \\$5 AOV increase)   | Aftersell case studies  |  
| Conversion Rates               | Significant improvements through personalized recommendations (e.g., 50% increase)    | Banking and retail case studies  |  
| Customer Retention             | Enhanced retention driven by tailored, relevant cross-sell offers   | E-commerce success stories          |  

This data-driven approach allows retailers to understand not only what products to recommend but also the context in which such recommendations should be delivered for maximum impact.  

---  

## 8. Implementation Best Practices for Data Mining in Sales Optimization  

Deploying data mining effectively to boost cross-selling and upselling requires a structured approach that integrates technology, process improvements, and continuous training. The following best practices have emerged from successful case studies and practical implementations:  

### 8.1 Establish Clear Business Objectives  
- **Define Specific Goals:** Start with well-defined objectives for what the data mining project should achieve—be it increasing cross-sell opportunities or enhancing upsell conversion rates. Clear goals ensure that the data mining process remains focused and actionable.  
- **Align Sales and Marketing Departments:** Ensure close collaboration between sales, marketing, and data teams to address internal silos and share success stories across domains.  

### 8.2 Invest in Data Quality and Integration  

- **Implement Robust Data Cleansing:** Quality data is the cornerstone of successful data mining. Regular cleansing, deduplication, and validation processes must be established to ensure accuracy.  
- **Integrate Diverse Data Sources:** Leverage integrated platforms that can assimilate data from CRM systems, transaction logs, and web analytics to provide a complete picture of customer behavior.  

### 8.3 Leverage Advanced Data Mining Techniques  

- **Adopt a Multi-Technique Approach:** Utilize a combination of association rule learning, clustering, regression, classification, and decision trees to gain a multidimensional insight into customer behavior.  
- **Invest in Real-time Analytics:** Implement solutions that support real-time data ingestion and analytics, enabling fast adjustments in sales strategies as market conditions evolve.  

### 8.4 Develop Customer-Centric Sales Collateral  

- **Evolve Traditional Case Studies:** Update existing sales materials to focus on business outcomes rather than just technical details. Integrate data mining insights to make case studies more engaging and relevant to customer pain points.  
- **Deliver Multi-format Content:** Ensure that sales collateral is accessible in multiple formats—from PDFs and slide decks to web-based interactive dashboards. This flexibility aids in quick dissemination and use during client meetings.  

### 8.5 Continuous Training and Enablement  

- **Ongoing Sales Training:** Regular training sessions on how to interpret data mining outputs, leverage predictive analytics, and deploy personalized sales strategies are critical. This empowers sales teams to become more proactive in their approach.  
- **Feedback Loops:** Incorporate mechanisms for continuous feedback and performance tracking. Regularly review campaign performance, update strategies accordingly, and encourage a culture of data-driven decision-making.  

### 8.6 Technology and BI Integration  

- **Invest in Integrated BI Platforms:** Use modern BI tools that seamlessly integrate with data mining systems. These platforms should offer intuitive dashboards, real-time analytics, and easy data visualization capabilities that are accessible to all stakeholders.  
- **Maintain Compliance and Governance:** With stringent regulations on data privacy and client confidentiality, it is essential to institute robust data governance policies. This protects client data while ensuring that sales teams can leverage insights responsibly.  

The following Mermaid flowchart provides a high-level overview of an integrated framework for implementing data mining in sales optimization:  

```mermaid  
flowchart TD  
  A["Define Business Objectives"] --> B["Data Collection & Integration"]  
  B --> C["Data Cleansing & Transformation"]  
  C --> D["Apply Multiple Data Mining Techniques"]  
  D --> E["Generate Insights & Build Predictive Models"]  
  E --> F["Segment Customers & Develop Targeted Strategies"]  
  F --> G["Deploy Multi-format Sales Collateral"]  
  G --> H["Implement Continuous Training and Feedback"]  
  H --> I["Monitor & Refine Sales Strategies"]  
  I --> END[END]  
```  

**Figure: Integrated Framework for Data Mining in Sales Optimization**  
This diagram captures the cyclical process from defining objectives to monitoring and refining strategies, embodying a continuous improvement model for driving cross-selling and upselling through data mining.  

---  

## 9. Conclusions and Future Trends  

Data mining has emerged as a transformative technology for boosting cross-selling and upselling by providing deep, actionable insights into customer behavior. The integration of advanced analytical techniques with sales processes not only enables companies to overcome longstanding challenges such as internal silos and outdated collateral but also drives measurable improvements in conversion rates and revenue growth.  

### Key Takeaways  

- **Enhanced Sales Efficiency:** Data mining helps break down internal silos and unifies disparate datasets into actionable sales insights, leading to improved pre-sales efficiency and optimized targeting.  
- **Personalized Customer Engagement:** Techniques such as clustering and association rule learning enable companies to deliver personalized product recommendations that resonate with customer needs and significantly boost average order values.  
- **Robust Predictive Analytics:** Regression and classification models provide reliable forecasts which facilitate informed decision-making, ultimately reducing sales cycle times and driving higher conversion rates.  
- **Operational Transformation:** Real-world case studies in IT/ITES, banking, telecom, and retail demonstrate transformative results—from a 50% conversion increases in banking to a doubling of cross-sell pitches in telecom.  

### Future Trends  

- **Integration of AI in BI Platforms:** The next generation of BI tools is set to integrate deeper AI and ML capabilities, allowing for even more accurate predictions and real-time optimization of sales strategies.  
- **Expansion of Real-Time Analytics:** The increasing demand for responsiveness will drive the adoption of platforms capable of real-time data integration and analysis, ensuring that sales teams can swiftly adapt to market changes.  
- **Greater Personalization:** As data mining techniques continue to evolve, the ability to offer hyper-personalized experiences in cross-selling and upselling will become a key competitive differentiator.  
- **Increased Focus on Data Governance:** With growing regulatory oversight on data privacy, there will be increased emphasis on strict data governance and ethical use of customer data, ensuring compliance while still reaping actionable insights.  

---  

## 10. References and Acknowledgments  

This report is compiled from multiple industry sources that investigate the intersection of data mining with cross-selling and upselling strategies. The key references include:  

- **Boosting Sales Through Case Studies: Cross-Selling and Upselling ...** – Detailed discussion on internal challenges and the value of effective case studies in IT/ITES sectors .  
- **Guide to Data Mining: Benefits, Examples, Techniques - Domo** – Comprehensive outline of data mining techniques and their applications across various industries .  
- **Data Mining in 2024: Latest Trends Reshaping Business Intelligence** – Insights on the future of BI, predictive analytics, and real-time data processing .  
- **How Is Data Mining Used in Business? - Tulane University** – Overview of the data mining process from goal definition to actionable insights .  
- **Case Study: How a global bank increased cross-selling ...** – A practical case study illustrating the bank's successful use of data analytics and behavioral science to boost upselling .  
- **US Telecom Giant Uses Analytics to Increase Cross-selling** – An in-depth case demonstrating how telecom companies leverage customer intelligence solutions to optimize cross-selling .  
- **7 Examples of Effective Cross-selling (and Why They Work)** – Best practice guide with examples illustrating effective cross-selling strategies and incremental revenue gains .  
- **Aftersell case studies - Customer success stories** – Illustrative success stories from e-commerce brands that effectively increased AOV and revenue through post-purchase upselling strategies .  

---  

## Final Summary of Main Findings  

- **Actionable Insights:** Data mining transforms raw data into actionable insights that enable effective cross-selling and upselling by identifying latent opportunities and customer pain points.  
- **Improved Sales Narratives:** By integrating business context and customer-centric case studies into sales collateral, organizations enhance both pre-sales efficiency and overall sales performance.  
- **Case Study Success:** Real-world examples across IT/ITES, banking, telecom, and retail sectors illustrate measurable improvements—from 50% conversion increases to doubling of cross-sell pitches—demonstrating the tangible impact of advanced analytics.  
- **Future Readiness:** The future of cross-selling and upselling lies in further integration of AI, real-time analytics, and hyper-personalization, balanced with strong data governance frameworks to protect customer privacy.  

By adopting the practices highlighted in this report, organizations can harness the power of data mining to not only overcome the challenges of traditional sales processes but also secure long-term competitive advantage in an increasingly data-driven market.  

---  

This comprehensive analysis demonstrates how data mining is catalyzing transformation in cross-selling and upselling initiatives, offering a blueprint for businesses aiming to enhance customer engagement and drive sustainable revenue growth.  

{/text}"""
]

if __name__ == "__main__":
    benchmark = ModelBenchmark()
    
    print("Starting Enhanced Model Benchmark...")
    print("This will measure tokens per second plus system metrics for each model.")
    
    # Run benchmark with enhanced metrics
    results = benchmark.run_benchmark(test_prompts, runs_per_prompt=3)
    
    # Print summary to console
    benchmark.print_summary(results)
    
    # Generate timestamp for filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save detailed results with timestamp
    results_filename = f"enhanced_benchmark_results-{timestamp}.json"
    with open(results_filename, "w") as f:
        json.dump(results, f, indent=2)
    
    # Generate and save report with timestamp
    report = benchmark.generate_report(results)
    report_filename = f"enhanced_benchmark_report-{timestamp}.md"
    with open(report_filename, "w") as f:
        f.write(report)
    
    print("\nEnhanced benchmark complete!")
    print(f"Detailed results saved to: {results_filename}")
    print(f"Report saved to: {report_filename}")
