import pytest
from unittest.mock import Mock, patch, create_autospec
from collections import OrderedDict
from logging import Logger
from aimq.worker import Worker, WorkerThread
from aimq.queue import Queue
from aimq.logger import Logger as AimqLogger
from langchain.schema.runnable import Runnable, RunnableLambda
import threading
import time

@pytest.fixture
def mock_logger():
    logger = create_autospec(AimqLogger, instance=True)
    logger.print = Mock()  # Add print method
    return logger

@pytest.fixture
def worker(mock_logger):
    worker = Worker()
    worker.logger = mock_logger
    return worker

def test_worker_initialization():
    """Test worker initializes with default values"""
    worker = Worker()
    assert isinstance(worker.queues, OrderedDict)
    assert len(worker.queues) == 0
    assert worker.is_running is not None
    assert worker.thread is None

@patch('aimq.worker.Queue')
def test_assign_task(mock_queue, worker):
    """Test assigning a task to the worker"""
    def dummy_task(x): return x
    runnable = RunnableLambda(dummy_task, name="test_queue")
    
    worker.assign(runnable, timeout=60)
    
    mock_queue.assert_called_once_with(
        runnable=runnable,
        timeout=60,
        tags=[],
        delete_on_finish=False,
        logger=worker.logger,
        worker_name=worker.name
    )
    assert "test_queue" in worker.queues
    worker.logger.info.assert_called_once_with("Registered task test_queue")

@patch('aimq.worker.Queue')
def test_task_decorator(mock_queue, worker):
    """Test task decorator functionality"""
    @worker.task(queue="test_decorator", timeout=30)
    def dummy_task(x):
        return x
    
    mock_queue.assert_called_once()
    assert "test_decorator" in worker.queues

def test_send_message(worker):
    """Test sending a message to a queue"""
    queue_mock = Mock()
    worker.queues["test_queue"] = queue_mock
    data = {"key": "value"}
    
    worker.send("test_queue", data)
    
    queue_mock.send.assert_called_once_with(data, None)

@patch('aimq.worker.WorkerThread')
def test_start_stop_worker(mock_thread_class, worker):
    """Test starting and stopping the worker"""
    mock_thread = Mock()
    mock_thread_class.return_value = mock_thread
    
    worker.start(block=False)
    assert worker.is_running.is_set()
    assert worker.thread is not None
    mock_thread.start.assert_called_once()
    
    worker.stop()
    assert not worker.is_running.is_set()
    mock_thread.join.assert_called_once()
    worker.logger.info.assert_called_with("Worker stopped")

@patch('aimq.worker.WorkerThread')
def test_start_already_running(mock_thread_class, worker):
    """Test starting an already running worker"""
    mock_thread = Mock()
    mock_thread_class.return_value = mock_thread
    mock_thread.is_alive.return_value = True
    
    worker.start(block=False)
    initial_thread = worker.thread
    
    # Try to start again
    worker.start(block=False)
    
    # Should still be using the same thread
    assert worker.thread == initial_thread
    assert mock_thread_class.call_count == 1

@pytest.mark.asyncio
async def test_work_queue(worker):
    """Test working a specific queue"""
    queue_mock = Mock()
    worker.queues["test_queue"] = queue_mock
    
    worker.work("test_queue")
    queue_mock.work.assert_called_once()

def test_task_decorator_with_custom_name(worker):
    """Test task decorator with a custom queue name"""
    @worker.task(queue="custom_queue")
    def task_function(x):
        return x * 2

    assert "custom_queue" in worker.queues
    assert worker.queues["custom_queue"].runnable.name == "custom_queue"

def test_task_decorator_with_default_name(worker):
    """Test task decorator using function name as queue name"""
    @worker.task()
    def task_function(x):
        return x * 2

    assert "task_function" in worker.queues
    assert worker.queues["task_function"].runnable.name == "task_function"

def test_send_with_delay(worker):
    """Test sending a message with delay"""
    queue_mock = Mock()
    worker.queues["test_queue"] = queue_mock
    data = {"key": "value"}
    delay = 60
    
    worker.send("test_queue", data, delay)
    queue_mock.send.assert_called_once_with(data, delay)

def test_send_to_nonexistent_queue(worker):
    """Test sending to a queue that doesn't exist raises KeyError"""
    with pytest.raises(KeyError):
        worker.send("nonexistent_queue", {})

def test_work_nonexistent_queue(worker):
    """Test working a queue that doesn't exist raises KeyError"""
    with pytest.raises(KeyError):
        worker.work("nonexistent_queue")

@patch('aimq.worker.load_module')
def test_load_worker_success(mock_load_module, tmp_path):
    """Test successfully loading a worker from a file"""
    mock_module = Mock()
    mock_worker = Mock(spec=Worker)
    mock_worker.logger = Mock()
    mock_module.worker = mock_worker
    mock_load_module.return_value = mock_module
    
    worker_path = tmp_path / "worker.py"
    worker_path.touch()
    
    loaded_worker = Worker.load(worker_path)
    assert loaded_worker == mock_worker
    mock_worker.logger.info.assert_called_once()

@patch('aimq.worker.load_module')
def test_load_worker_missing_attribute(mock_load_module, tmp_path):
    """Test loading a worker file without worker attribute"""
    mock_module = Mock(spec=[])
    mock_load_module.return_value = mock_module
    
    worker_path = tmp_path / "worker.py"
    worker_path.touch()
    
    with pytest.raises(AttributeError, match="does not export a 'worker' attribute"):
        Worker.load(worker_path)

def test_log_method(worker):
    """Test the log method"""
    worker.log(block=True)
    worker.logger.print.assert_called_once_with(block=True, level=worker.log_level)

def test_worker_thread_run(mock_logger):
    """Test the WorkerThread run method"""
    running = threading.Event()
    running.set()
    queues = OrderedDict()
    
    # Mock queue that will process one job then have no more
    queue_mock = Mock(spec=Queue)
    queue_mock.name = "test_queue"
    first_call = threading.Event()
    second_call = threading.Event()
    call_count = 0
    
    def work_side_effect():
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            first_call.set()
            return True
        if call_count == 2:
            second_call.set()
            return False
        return False
    
    queue_mock.work.side_effect = work_side_effect
    queues["test_queue"] = queue_mock
    
    thread = WorkerThread(queues, mock_logger, running, idle_wait=0.01)
    
    # Start thread and wait for both calls
    thread.start()
    first_call.wait(timeout=1.0)
    second_call.wait(timeout=1.0)
    running.clear()
    thread.join(timeout=1.0)
    
    assert queue_mock.work.call_count >= 2
    mock_logger.info.assert_called_with("Worker thread started")
    mock_logger.debug.assert_called_with("No jobs found, waiting...")

def test_worker_thread_exception_handling(mock_logger):
    """Test WorkerThread handles exceptions properly"""
    running = threading.Event()
    running.set()
    queues = OrderedDict()
    
    # Mock queue that raises an exception
    queue_mock = Mock(spec=Queue)
    queue_mock.name = "test_queue"
    queue_mock.work.side_effect = RuntimeError("Test error")
    queues["test_queue"] = queue_mock
    
    thread = WorkerThread(queues, mock_logger, running, idle_wait=0.1)
    
    # Start thread and let it run briefly
    thread.start()
    time.sleep(0.2)
    running.clear()
    thread.join()
    
    mock_logger.error.assert_called_with(
        "Runtime error in queue test_queue",
        {"error": "Test error"}
    )

def test_worker_thread_critical_error(mock_logger):
    """Test WorkerThread handles critical errors properly"""
    running = threading.Event()
    running.set()
    queues = OrderedDict()
    error_raised = threading.Event()
    
    # Mock queue that raises an unexpected exception
    queue_mock = Mock(spec=Queue)
    queue_mock.name = "test_queue"
    def work_side_effect():
        error_raised.set()
        raise Exception("Unexpected error")
    queue_mock.work.side_effect = work_side_effect
    queues["test_queue"] = queue_mock
    
    thread = WorkerThread(queues, mock_logger, running, idle_wait=0.01)
    
    # Start thread and wait for error
    thread.start()
    error_raised.wait(timeout=1.0)
    thread.join(timeout=1.0)
    
    mock_logger.critical.assert_called_with(
        "Worker thread encountered an unhandled error",
        {"error": "Unexpected error"}
    )
    assert not running.is_set()

def test_worker_name_from_config():
    """Test worker name is set from config"""
    with patch('aimq.worker.config') as mock_config:
        mock_config.worker_name = "test_worker"
        worker = Worker()
        assert worker.name == "test_worker"

def test_task_decorator_function():
    """Test task decorator function"""
    worker = Worker()
    
    @worker.task()
    def task_function(x):
        return x * 2
    
    assert isinstance(task_function, type(lambda: None))
    result = task_function(5)
    assert result == 10

def test_worker_start_blocking():
    """Test worker start with blocking"""
    worker = Worker()
    worker.logger = create_autospec(AimqLogger, instance=True)
    worker.logger.print = Mock()
    
    # Mock the thread to avoid actual execution
    with patch('aimq.worker.WorkerThread') as mock_thread_class:
        mock_thread = Mock()
        mock_thread_class.return_value = mock_thread
        
        # Start worker in blocking mode
        worker.start(block=True)
        
        mock_thread.start.assert_called_once()
        worker.logger.print.assert_called_once_with(block=True, level=worker.log_level)

def test_worker_thread_error_handling():
    """Test worker thread error handling"""
    running = threading.Event()
    running.set()
    queues = OrderedDict()
    logger = create_autospec(AimqLogger, instance=True)
    error_raised = threading.Event()
    
    # Mock queue that raises a RuntimeError
    queue_mock = Mock(spec=Queue)
    queue_mock.name = "test_queue"
    def work_side_effect():
        error_raised.set()
        raise RuntimeError("Test error")
    queue_mock.work.side_effect = work_side_effect
    queues["test_queue"] = queue_mock
    
    thread = WorkerThread(queues, logger, running, idle_wait=0.01)
    
    # Start thread and wait for error
    thread.start()
    error_raised.wait(timeout=1.0)
    running.clear()
    thread.join(timeout=1.0)
    
    logger.error.assert_called_with(
        "Runtime error in queue test_queue",
        {"error": "Test error"}
    )
