# Async Task Manager

A flexible and efficient Python library for managing asynchronous tasks with configurable execution strategies. This library provides multiple built-in strategies for controlling task execution flow, including concurrent limits, delays, and rate limiting.

## Features

- 🚀 **Multiple Execution Strategies**: Built-in support for concurrent limits, delayed execution, and fixed-window rate limiting
- 🔧 **Extensible Architecture**: Easy to create custom strategies by extending the base strategy class
- ⚡ **High Performance**: Efficient task scheduling with minimal overhead
- 🛡️ **Type Safe**: Full type hints support with Python 3.7+
- 📊 **Task Metadata**: Support for attaching metadata to tasks for tracking and debugging
- 🔄 **Non-blocking**: Fully asynchronous with proper resource management

## Requirements

- Python 3.7+
- No external dependencies (uses only standard library)

## Installation

```bash
git clone https://github.com/mamahoos/async-task-manager.git
cd async-task-manager
```

## Quick Start

```python
import asyncio
from async_task_manager import TaskManager
from async_task_manager.strategies.concurrent_limit import ConcurrentLimitStrategy


async def sample_task(name: str, delay: float):
    await asyncio.sleep(delay)
    print(f"Task {name} completed after {delay}s")
    return f"Result from {name}"


async def main():
    # Create a strategy that limits concurrent tasks to 3
    strategy = ConcurrentLimitStrategy(max_concurrent=3)
    manager  = TaskManager(strategy, poll_interval=0.2)

    # Add 8 tasks
    for i in range(8):
        manager.add_task(sample_task(f"task-{i}", 1.0))

    # Start the manager in the background
    await manager.idle()

    # Let it run for 10 seconds
    await asyncio.sleep(10)

    print("Stopping the manager...")
    await manager.stop()

    print("Manager stopped.")


if __name__ == "__main__":
    asyncio.run(main())
```

## Available Strategies

### 1. ConcurrentLimitStrategy ✅

**Purpose**: Controls system resource usage by limiting concurrent executions, preventing memory exhaustion and connection pool overflow.

**Use Cases:**
- **Database Operations**: Prevent overwhelming database connection pools
- **File Processing**: Avoid hitting OS file descriptor limits when processing large numbers of files
- **Memory-Intensive Tasks**: Control memory usage when processing large datasets
- **Network Requests**: Manage concurrent HTTP requests to prevent socket exhaustion

```python
from async_task_manager.strategies import ConcurrentLimitStrategy

# Example: Processing large files without overwhelming the system
strategy = ConcurrentLimitStrategy(max_concurrent=5)

async def process_large_file(file_path: str):
    # Heavy file processing that uses significant memory
    with open(file_path, 'rb') as f:
        data = f.read()  # Large memory allocation
        # Process data...
        ...

# Only 5 files will be processed simultaneously
for file_path in large_file_list:
    manager.add_task(
        process_large_file(file_path)
    )
```

**Parameters:**
- `max_concurrent` (int): Maximum number of tasks running simultaneously

---

### 2. DelayedStrategy ✅

**Purpose**: Ensures minimum time intervals between task executions, useful for systems that need breathing room or have temporal constraints.

**Use Cases:**
- **System Recovery**: Allow systems to recover between intensive operations
- **Log Processing**: Prevent log file locks by spacing out log operations
- **Batch Operations**: Ensure database transactions have time to commit
- **Resource Cleanup**: Give garbage collector time to work between memory-intensive tasks
- **Avoiding System Overload**: Prevent CPU spikes in production environments

```python
from async_task_manager.strategies import DelayedStrategy

# Example: Database backup operations that need recovery time
strategy = DelayedStrategy(delay_seconds=30.0)

async def backup_table(table_name: str):
    # Heavy database operation that locks tables
    await db.backup_table(table_name)
    return f"Backed up {table_name}"

# Each backup waits 30 seconds after the previous one completes
for table in database_tables:
    manager.add_task(
        backup_table(table)
    )
```

**Parameters:**
- `delay_seconds` (float): Minimum delay between task executions

---

### 3. FixedWindowStrategy ✅

**Purpose**: Implements rate limiting to comply with external API limits, preventing rate limit errors and service bans.

**Use Cases:**
- **API Integration**: Respect third-party API rate limits (Twitter: 300 requests/15min, Telegram: 30 requests/second)
- **Web Scraping**: Avoid getting banned by respecting website rate limits
- **Payment Processing**: Respect payment gateway limits

```python
from async_task_manager.strategies import FixedWindowStrategy

# Example: Twitter API integration (300 requests per 15 minutes)
strategy = FixedWindowStrategy(max_requests=300, window_seconds=900)  # 15 minutes

async def fetch_tweets(user_id: str):
    # Call to Twitter API
    response = await twitter_client.get_user_tweets(user_id)
    return response.data

# Automatically respects Twitter's rate limits
for user_id in user_list:
    manager.add_task(
        fetch_tweets(user_id)
    )
```

**Parameters:**
- `max_requests` (int): Maximum number of tasks per window
- `window_seconds` (float): Duration of each window in seconds

## Advanced Usage

### Creating Custom Strategies

You can create custom strategies by extending the `BaseStrategy` class:

```python
from async_task_manager.strategies.base import BaseStrategy
from async_task_manager.task import Task
from typing import Optional
from collections import deque

class CustomStrategy(BaseStrategy):
    def __init__(self):
        self.tasks = deque()
    
    def add_task(self, task: Task) -> None:
        self.tasks.append(task)
    
    def get_next_task(self) -> Optional[Task]:
        return self.tasks.popleft() if self.tasks else None
    
    async def get_sleep_interval(self) -> Optional[float]:
        return 0.1  # Sleep for 100ms between checks
    
    async def on_task_done(self) -> None:
        # Custom cleanup logic here
        pass
```

### Task Metadata and Results

Tasks support metadata and result retrieval:

```python
async def example_with_metadata():
    manager = TaskManager(custom_strategy)      # At first, define your Custom Strategy
    
    async def worker_task(data: str):
        await asyncio.sleep(1)
        return f"Processed: {data}"
    
    # Add task with metadata
    task_coro = worker_task("important_data")
    metadata = {
        "priority"  : "high",
        "created_at": time.time(),
        "category"  : "data_processing"
    }
    
    manager.add_task(task_coro, metadata)
    
    # Tasks can be awaited for results if needed
    # (Note: This requires keeping a reference to the Task object)
```

## API Reference

### TaskManager

Main class for managing task execution.

#### Constructor

```python
TaskManager(strategy: BaseStrategy, poll_interval: float = 0.01)
```

**Parameters:**
- `strategy`: Execution strategy to use
- `poll_interval`: Polling interval in seconds (default: 0.01)

#### Methods

- `add_task(coro: Awaitable[Any], metadata: Optional[Dict[str, Any]] = None) -> None`
- `async run() -> None`: Start processing tasks
- `async idle() -> None`: Stater processing tasks non-blocking
- `async stop() -> None`: Stop the task manager

### Task

Represents an asynchronous task with optional metadata.

#### Constructor

```python
Task(coro: Awaitable[Any], metadata: Optional[Dict[str, Any]] = None)
```

#### Methods

- `async run() -> Any`: Execute the task
- `async wait() -> Any`: Wait for task completion and get result

### BaseStrategy

Abstract base class for all execution strategies.

#### Abstract Methods

- `add_task(task: Task) -> None`
- `get_next_task() -> Optional[Task]`
- `async get_sleep_interval() -> Optional[float]`

#### Optional Methods

- `async on_task_done() -> None`: Called when a task completes

## Project Structure

```
async_task_manager/
├── __init__.py
├── manager.py              # TaskManager implementation
├── task.py                 # Task class definition
└── strategies/
    ├── __init__.py
    ├── base.py             # BaseStrategy abstract class
    ├── concurrent_limit.py # ConcurrentLimitStrategy
    ├── delayed.py          # DelayedStrategy
    └── fixed_window.py     # FixedWindowStrategy
```

## Strategy Development Roadmap

### ✅ Implemented Strategies

- **✅ ConcurrentLimitStrategy** - Controls concurrent task execution for resource management
- **✅ DelayedStrategy** - Enforces minimum delays between task executions
- **✅ FixedWindowStrategy** - Implements fixed-window rate limiting for API compliance

### 🚧 Planned Strategies

- **⏳ RetryStrategy** - Automatically retries failed tasks with exponential backoff
  - *Use Case*: Network requests, database operations, external service calls
  - *Features*: Configurable max retries, backoff algorithms, failure conditions
  
- **⏳ PriorityQueueStrategy** - Executes tasks based on priority levels
  - *Use Case*: Job processing systems, critical vs non-critical operations
  - *Features*: Multiple priority levels, priority inheritance, starvation prevention
  
- **⏳ SlidingWindowStrategy** - Advanced rate limiting with sliding time windows
  - *Use Case*: More precise rate limiting than fixed windows
  - *Features*: Smoother request distribution, better burst handling
  
- **⏳ AdaptiveStrategy** - Dynamically adjusts execution based on system performance
  - *Use Case*: Auto-scaling applications, performance-sensitive systems
  - *Features*: CPU/memory monitoring, automatic concurrency adjustment
  
- **⏳ BulkStrategy** - Batches multiple tasks for bulk operations
  - *Use Case*: Database bulk inserts, batch API calls, file operations
  - *Features*: Configurable batch sizes, timeout handling, partial failure recovery
  
- **⏳ CircuitBreakerStrategy** - Fails fast when downstream services are unavailable
  - *Use Case*: Microservices, external API dependencies
  - *Features*: Failure threshold detection, recovery mechanisms, health checks
  
- **⏳ WeightedRoundRobinStrategy** - Distributes tasks across resources with weights
  - *Use Case*: Load balancing, multi-server deployments
  - *Features*: Server weight configuration, health-based routing
  
- **⏳ TimeBasedStrategy** - Schedules tasks for specific times or intervals
  - *Use Case*: Cron-like scheduling, maintenance tasks, periodic operations
  - *Features*: Cron expressions, timezone support, missed execution handling

### 🎯 Strategy Contribution Guidelines

If you've developed a custom strategy and believe it would benefit the community, please consider contributing! We welcome strategies that meet these criteria:

#### High-Value Contributions
- **🌟 Broad Applicability**: Solves common problems faced by many developers
- **🌟 Production Ready**: Well-tested, handles edge cases, includes comprehensive error handling
- **🌟 Performance Optimized**: Minimal overhead, efficient resource usage
- **🌟 Well Documented**: Clear use cases, examples, and API documentation

#### Technical Requirements
- **✅ Type Hints**: Full type annotation support
- **✅ Thread Safety**: Proper async/await patterns and resource locking
- **✅ Error Handling**: Graceful failure modes and recovery mechanisms
- **✅ Configuration Validation**: Input validation with meaningful error messages
- **✅ Memory Efficient**: No memory leaks, proper cleanup in `on_task_done()`

#### Documentation Standards
- **📚 Real-world Examples**: Practical use cases with code samples
- **📚 Performance Characteristics**: Time/space complexity information
- **📚 Integration Guide**: How to use with existing strategies
- **📚 Testing Coverage**: Unit tests and integration test examples

#### Architectural Alignment
- **🏗️ Strategy Pattern**: Follows existing `BaseStrategy` interface
- **🏗️ Single Responsibility**: Focused on one specific execution pattern
- **🏗️ Composability**: Works well with other strategies if applicable
- **🏗️ Backwards Compatibility**: Doesn't break existing functionality

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions:

1. Search [existing issues](https://github.com/mamahoos/async-task-manager/issues)
2. Create a [new issue](https://github.com/mamahoos/async-task-manager/issues/new)

---
