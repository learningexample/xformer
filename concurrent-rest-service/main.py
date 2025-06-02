from fastapi import FastAPI
import asyncio
import random
import time
import logging

from starlette.responses import StreamingResponse


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI()

async def simulated_service(service_name: str):
    """Simulate an async service with random delay"""
    wait_time = random.uniform(1, 5)  # Random wait time between 1 to 5 seconds
    logging.info(f"Starting {service_name}, will take {wait_time:.2f} seconds")
    
    await asyncio.sleep(wait_time)  # Simulate work
    
    end_time = time.time()
    logging.info(f"Completed {service_name} in {wait_time:.2f} seconds")
    
    return {
        "service": service_name,
        "response_time": wait_time,
        "timestamp": end_time
    }

@app.get("/simulate_concurrency")
async def simulate_concurrent_requests():
    """Runs all services concurrently (total time ≈ max(t1, t2, t3))"""
    services = ["service1", "service2", "service3"]

    logging.info("Starting all services concurrently...")
    start_time = time.time()

    results = await asyncio.gather(*(simulated_service(service) for service in services))

    end_time = time.time()
    total_elapsed = end_time - start_time
    logging.info(f"All services completed in {total_elapsed:.2f} seconds")

    return {
        "services": results,
        "total_time": total_elapsed,
        "summary": "This demonstrates concurrent execution"
    }

@app.get("/simulate_serial")
async def simulate_serial_requests():
    """Runs all services serially (total time = t1 + t2 + t3)"""
    services = ["service1", "service2", "service3"]

    logging.info("Starting all services serially...")
    start_time = time.time()

    results = []
    for service in services:
        result = await simulated_service(service)  # Calls sequentially
        results.append(result)

    end_time = time.time()
    total_elapsed = end_time - start_time
    logging.info(f"All services completed in {total_elapsed:.2f} seconds")

    return {
        "services": results,
        "total_time": total_elapsed,
        "summary": "This demonstrates serialized execution"
    }


async def stream_service(service_name: str):
    """Simulate an async service with random delay for streaming"""
    wait_time = random.uniform(1, 5)  # Random wait time between 1 to 5 seconds
    start_time = time.time()
    
    await asyncio.sleep(wait_time)  # Simulate processing delay
    
    response_time = time.time() - start_time
    return f'{{"service": "{service_name}", "response_time": {response_time:.2f}}}\n'

async def event_stream():
    services = ["service1", "service2", "service3"]
    tasks = [stream_service(service) for service in services]
    
    for task in asyncio.as_completed(tasks):  # Process results as they complete
        result = await task
        yield result  # Send data incrementally

@app.get("/stream")
async def stream_responses():
    """Send responses to the frontend as they become available"""
    return StreamingResponse(event_stream(), media_type="text/event-stream")
