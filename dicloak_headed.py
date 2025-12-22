import asyncio
import logging
import time
import requests
from playwright.async_api import async_playwright, Page
import os
from typing import Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandle('browser_control.log', encoding='utf-8'),  # Write to file
        logging.StreamHandler()  # Output to console
    ]
)
logger = logging.getLogger(__name__)

# API endpoints and key
OPEN_ENV_URL = "https://api.dicloak.com/v2/env/open_env  "
CLOSE_ENV_URL = "https://api.dicloak.com/v2/env/close_env  "
X_API_KEY = "F0XXXX7C-68XX-11ED-A2XX-00163E019798"  # Replace with your actual key

# Create screenshot directory if it doesn't exist
SCREENSHOT_DIR = "screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# Define custom exception class for different error types
class BrowserAPIError(Exception):
    """Custom exception for errors during browser API interaction"""
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"API Error [{code}]: {message}")

async def open_browser_session() -> Tuple[Optional[str], Optional[str]]:
    """
    Call /open_env API to get a new browser session ID and CDP URL.
    Returns (session_id, cdp_url) on success.
    On failure, logs error and returns (None, None), or raises custom exception.
    """
    headers = {
        "X-API-KEY": X_API_KEY,
        "Content-Type": "application/json"
    }
    try:
        # Send PATCH request
        response = requests.patch(OPEN_ENV_URL, headers=headers, timeout=30)  # Add timeout
        response.raise_for_status()  # Check HTTP status

        # Parse JSON response
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            logger.error(f"API response is not valid JSON: {response.text}")
            return None, None

        # Get business status code and message
        code = data.get('code')
        message = data.get('msg', 'Unknown error')

        # Check if business logic succeeded
        if code == 0:
            session_id = data['data']['session_id']
            cdp_url = data['data']['url']
            logger.info(f"Successfully obtained new session: session_id={session_id}, CDP URL={cdp_url}")
            return session_id, cdp_url
        else:
            # Handle known error codes
            error_messages = {
                300104: "Proxy configuration exhausted. Please update proxy settings. (Occurs when proxy_way=USE_ONE and all proxies are used up)",
                300105: "Too many browser instances launched. Please close some before retrying.",
                300106: "Cloud browser error: failed to start browser instance (often due to invalid proxy configuration)",
                300000: "Business exception: system error"
            }
            detailed_message = error_messages.get(code, f"Unknown error: {message}")
            logger.error(f"Open session response: {message}")
            logger.error(f"Failed to obtain session: [{code}] {detailed_message}")
            return None, None

    except requests.exceptions.Timeout:
        logger.error("Request timed out. Please check network or API service status")
        return None, None
    except requests.exceptions.ConnectionError:
        logger.error("Network connection error. Please check network or API URL")
        return None, None
    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP request error: {e}")
        return None, None
    except KeyError as e:
        logger.error(f"API response missing required field: {e}")
        return None, None
    except Exception as e:
        logger.error(f"Unexpected error while obtaining session: {e}")
        return None, None

async def close_browser_session(session_id: str) -> bool:
    """
    Call /close_env API to close the specified browser session
    :param session_id: ID of the session to close
    :return: True on success, False on failure
    """
    if not session_id:
        logger.warning("Attempted to close empty session ID")
        return False

    headers = {
        "X-API-KEY": X_API_KEY,
        "Content-Type": "application/json"
    }
    try:
        # Assume session_id is passed in request body (adjust per actual API spec)
        payload = {"session_id": session_id}
        response = requests.patch(CLOSE_ENV_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()

        data = response.json()
        if data.get('code') == 0:
            logger.info(f"Successfully closed session: session_id={session_id}")
            return True
        else:
            logger.error(f"Failed to close session: [{data.get('code')}] {data.get('msg')}")
            return False

    except Exception as e:
        logger.error(f"Failed to close session: {e}")
        return False

async def take_screenshot_with_playwright(cdp_url: str, screenshot_path: str):
    """
    Use Playwright to connect to CDP URL, navigate to webpage, and take screenshot
    :param cdp_url: CDP WebSocket URL
    :param screenshot_path: Full path and filename to save screenshot
    """
    async with async_playwright() as p:
        browser = None
        page = None
        try:
            # Launch browser via CDP connection
            browser = await p.chromium.connect_over_cdp(cdp_url)
            page = await browser.new_page()

            # Navigate to target website (fixed trailing space)
            await page.goto("https://ip111.cn/")
            logger.info("Navigated to https://ip111.cn/")

            # Wait for page to load (optional: ensure content is rendered)
            await page.wait_for_timeout(2000)  # or use await page.wait_for_load_state("networkidle")

            # Take screenshot
            await page.screenshot(path=screenshot_path, full_page=True)  # Screenshot full page
            logger.info(f"Screenshot saved to: {screenshot_path}")

        except Exception as e:
            logger.error(f"Playwright operation failed: {e}")
            raise
        finally:
            # Ensure resources are properly released
            if page:
                await page.close()
            if browser:
                await browser.close()

async def run_cycle(cycle_number: int) -> bool:
    """
    Execute one full cycle: open session → take screenshot → close session
    :param cycle_number: Current cycle number (1-6)
    :return: True on success, False on failure
    """
    logger.info(f"Starting cycle {cycle_number}...")
    session_id = None
    cdp_url = None

    try:
        # 1. Obtain new browser session
        session_id, cdp_url = await open_browser_session()
        if not session_id or not cdp_url:
            logger.error("Failed to obtain browser session; skipping this cycle")
            return False

        # Generate unique screenshot filename
        screenshot_filename = f"screenshot_{cycle_number:02d}.png"  # e.g., screenshot_01.png
        screenshot_path = os.path.join(SCREENSHOT_DIR, screenshot_filename)

        # 2. Control browser via Playwright and take screenshot
        await take_screenshot_with_playwright(cdp_url, screenshot_path)

        logger.info(f"Cycle {cycle_number} completed successfully")
        return True

    except Exception as e:
        logger.error(f"Exception during cycle {cycle_number}: {e}")
        return False
    finally:
        # 3. Always attempt to close session to prevent resource leaks
        if session_id:
            try:
                await close_browser_session(session_id)
            except Exception as close_error:
                logger.error(f"Error while closing session {session_id}: {close_error}")

async def main():
    """
    Main function: run specified number of cycles
    """
    total_cycles = 1  # Adjust as needed
    successful_cycles = 0

    for i in range(1, total_cycles + 1):
        success = await run_cycle(i)

        if success:
            successful_cycles += 1
            logger.info(f"Cycle {i} succeeded")
        else:
            logger.error(f"Cycle {i} failed")

        # Optional: add delay between cycles
        if i < total_cycles:
            delay_seconds = 2
            logger.info(f"Waiting {delay_seconds} seconds before next cycle...")
            await asyncio.sleep(delay_seconds)

    logger.info(f"All cycles completed. Success: {successful_cycles}/{total_cycles}")

if __name__ == "__main__":
    asyncio.run(main())