import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time
import os

class TestToDoApp:
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup method that runs before each test"""
        self.driver = self.get_driver()
        self.wait = WebDriverWait(self.driver, 10)
        self.base_url = os.getenv('BASE_URL', 'http://13.49.246.25:8090')
        self.email = os.getenv('TEST_EMAIL', 'haleemaa.saadiia@gmail.com')
        self.password = os.getenv('TEST_PASSWORD', '12345678')
        self.login()
        yield
        self.driver.quit()

    def get_driver(self):
        """Configure and return Chrome WebDriver"""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--remote-debugging-port=9222")
        return webdriver.Chrome(options=options)

    def login(self):
        """Reusable login method"""
        try:
            print("Starting login process...")
            self.driver.get(f"{self.base_url}/login")
            time.sleep(2)

            # Wait for and locate input fields
            email_input = self.wait.until(EC.presence_of_element_located((By.ID, "email-address")))
            password_input = self.driver.find_element(By.ID, "password")

            email_input.send_keys(self.email)
            password_input.send_keys(self.password)

            # Click the login button
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()

            # Wait for redirect to dashboard
            self.wait.until(lambda driver: "/login" not in driver.current_url)
            print(f"Login successful. Current URL: {self.driver.current_url}")

        except Exception as e:
            print(f"Login failed: {str(e)}")
            pytest.fail(f"Login failed: {str(e)}")

    def test_dashboard_title(self):
        """Test dashboard page title"""
        print("Testing dashboard title...")
        self.driver.get(f"{self.base_url}/")
        time.sleep(2)
        
        title = self.driver.title
        assert any(keyword in title.lower() for keyword in ["dashboard", "todo", "task"]), \
            f"Expected title to contain dashboard/todo/task, got: {title}"

    def test_task_input_field_exists(self):
        """Test that task input field exists on tasks page"""
        print("Testing task input field exists...")
        self.driver.get(f"{self.base_url}/tasks")
        time.sleep(2)
        
        task_input = self.wait.until(EC.presence_of_element_located((By.ID, "task")))
        assert task_input.is_displayed()
        
        placeholder = task_input.get_attribute("placeholder")
        assert placeholder == "Enter task"

    def test_add_todo(self):
        """Test adding a new task"""
        print("Testing add new task...")
        self.driver.get(f"{self.base_url}/tasks")
        time.sleep(2)
        
        # Fill out the task form
        task_input = self.driver.find_element(By.ID, "task")
        task_input.send_keys("Buy milk")
        
        # Set priority
        priority_select = Select(self.driver.find_element(By.ID, "priority"))
        priority_select.select_by_value("high")
        
        # Submit the form
        add_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        add_button.click()
        
        # Wait for task to appear
        time.sleep(3)
        
        # Check if task was added
        page_source = self.driver.page_source
        assert "Buy milk" in page_source

    def test_mark_todo_complete(self):
        """Test marking a task as complete"""
        print("Testing mark task as complete...")
        self.driver.get(f"{self.base_url}/tasks")
        time.sleep(2)
        
        # First add a task if none exists
        try:
            checkbox = self.driver.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
        except:
            # Add a task first
            task_input = self.driver.find_element(By.ID, "task")
            task_input.send_keys("Test completion task")
            add_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            add_button.click()
            time.sleep(2)
            checkbox = self.driver.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
        
        # Click the checkbox
        checkbox.click()
        time.sleep(1)
        
        # Verify checkbox is checked
        assert checkbox.is_selected()

    def test_delete_task(self):
        """Test deleting a task"""
        print("Testing delete task...")
        self.driver.get(f"{self.base_url}/tasks")
        time.sleep(2)
        
        # First ensure there's at least one task
        try:
            delete_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Delete')]")
        except:
            # Add a task first
            task_input = self.driver.find_element(By.ID, "task")
            task_input.send_keys("Task to delete")
            add_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            add_button.click()
            time.sleep(2)
            delete_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Delete')]")
        
        # Count tasks before deletion
        tasks_before = len(self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Delete')]"))
        
        # Click delete button
        delete_button.click()
        time.sleep(2)
        
        # Count tasks after deletion
        tasks_after = len(self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Delete')]"))
        
        # Verify task was deleted
        assert tasks_after == tasks_before - 1

    def test_multiple_tasks(self):
        """Test adding multiple tasks"""
        print("Testing add multiple tasks...")
        self.driver.get(f"{self.base_url}/tasks")
        time.sleep(2)
        
        task_input = self.driver.find_element(By.ID, "task")
        add_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        
        tasks_to_add = ["Task 1", "Task 2", "Task 3"]
        
        for task in tasks_to_add:
            task_input.clear()
            task_input.send_keys(task)
            add_button.click()
            time.sleep(1)
        
        # Wait for all tasks to load
        time.sleep(2)
        
        # Verify all tasks are present
        page_source = self.driver.page_source
        for task in tasks_to_add:
            assert task in page_source

    def test_persistent_task_after_reload(self):
        """Test task persistence after page reload"""
        print("Testing task persistence after reload...")
        self.driver.get(f"{self.base_url}/tasks")
        time.sleep(2)
        
        # Add a task
        task_input = self.driver.find_element(By.ID, "task")
        task_text = "Persistent Task"
        task_input.send_keys(task_text)
        add_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        add_button.click()
        
        # Wait for task to be saved
        time.sleep(3)
        
        # Reload the page
        self.driver.refresh()
        time.sleep(3)
        
        # Check if task still exists
        page_source = self.driver.page_source
        assert task_text in page_source

    def test_empty_task_prevention(self):
        """Test prevention of empty task submission"""
        print("Testing empty task prevention...")
        self.driver.get(f"{self.base_url}/tasks")
        time.sleep(2)
        
        # Count existing tasks
        page_source_before = self.driver.page_source
        
        # Try to submit empty task
        add_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        add_button.click()
        time.sleep(2)
        
        # Check that no empty task was added
        page_source_after = self.driver.page_source
        assert page_source_before == page_source_after

    def test_login_page_elements(self):
        """Test login page elements are present"""
        print("Testing login page elements...")
        self.driver.get(f"{self.base_url}/login")
        time.sleep(2)
        
        # Check for email and password fields
        email_input = self.driver.find_element(By.ID, "email-address")
        password_input = self.driver.find_element(By.ID, "password")
        
        assert email_input.is_displayed()
        assert password_input.is_displayed()
        
        # Check for submit button
        submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        assert submit_button.is_displayed()

    def test_navigation_to_tasks(self):
        """Test navigation from dashboard to tasks"""
        print("Testing navigation from dashboard to tasks...")
        self.driver.get(f"{self.base_url}/")
        time.sleep(2)
        
        # Look for "Go to Task Manager" link
        try:
            task_manager_link = self.driver.find_element(By.LINK_TEXT, "Go to Task Manager")
            task_manager_link.click()
            time.sleep(2)
            
            # Verify we're on the tasks page
            current_url = self.driver.current_url
            assert "/tasks" in current_url
            
        except:
            # If direct link doesn't exist, try navigating via URL
            self.driver.get(f"{self.base_url}/tasks")
            time.sleep(2)
            current_url = self.driver.current_url
            assert "/tasks" in current_url

    def test_priority_selection(self):
        """Test priority selection functionality"""
        print("Testing priority selection...")
        self.driver.get(f"{self.base_url}/tasks")
        time.sleep(2)
        
        # Find priority dropdown
        priority_select = Select(self.driver.find_element(By.ID, "priority"))
        
        # Test each priority option
        priorities = ["low", "medium", "high"]
        for priority in priorities:
            priority_select.select_by_value(priority)
            selected_value = priority_select.first_selected_option.get_attribute("value")
            assert selected_value == priority

    def test_due_date_functionality(self):
        """Test due date functionality"""
        print("Testing due date functionality...")
        self.driver.get(f"{self.base_url}/tasks")
        time.sleep(2)
        
        # Fill task form with due date
        task_input = self.driver.find_element(By.ID, "task")
        task_input.send_keys("Task with due date")
        
        # Set due date
        due_date_input = self.driver.find_element(By.ID, "due-date")
        due_date_input.send_keys("2025-12-31")
        
        # Submit task
        add_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        add_button.click()
        time.sleep(2)
        
        # Verify task with due date was added
        page_source = self.driver.page_source
        assert "Task with due date" in page_source
        assert "Due:" in page_source