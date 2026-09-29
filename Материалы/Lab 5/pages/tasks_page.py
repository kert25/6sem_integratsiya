"""
Page Object для страницы управления задачами
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from .base_page import BasePage


class TasksPage(BasePage):
    """Страница управления задачами"""
    
    # Локаторы
    NEW_TASK_INPUT = (By.ID, "new-task")
    ADD_TASK_BUTTON = (By.ID, "add-task-btn")
    TASK_LIST = (By.ID, "task-list")
    TASK_ITEMS = (By.CLASS_NAME, "task-item")
    TASK_CHECKBOX = (By.CLASS_NAME, "task-checkbox")
    TASK_TEXT = (By.CLASS_NAME, "task-text")
    DELETE_TASK_BUTTON = (By.CLASS_NAME, "delete-task")
    EDIT_TASK_BUTTON = (By.CLASS_NAME, "edit-task")
    FILTER_ALL = (By.ID, "filter-all")
    FILTER_ACTIVE = (By.ID, "filter-active")
    FILTER_COMPLETED = (By.ID, "filter-completed")
    CLEAR_COMPLETED = (By.ID, "clear-completed")
    TASK_COUNTER = (By.ID, "task-counter")
    NO_TASKS_MESSAGE = (By.ID, "no-tasks")
    
    def __init__(self, driver):
        super().__init__(driver)
        self.base_url = "http://localhost:8080/tasks"
    
    def open_tasks_page(self):
        """Открытие страницы задач"""
        self.open("/tasks")
    
    def create_task(self, task_text: str):
        """Создание новой задачи"""
        self.logger.info(f"Создание задачи: {task_text}")
        
        self.input_text(self.NEW_TASK_INPUT, task_text)
        self.click(self.ADD_TASK_BUTTON)
    
    def get_task_count(self) -> int:
        """Получение количества задач"""
        if self.is_element_present(self.TASK_ITEMS):
            return len(self.find_elements(self.TASK_ITEMS))
        return 0
    
    def get_task_texts(self) -> list:
        """Получение текстов всех задач"""
        tasks = []
        if self.is_element_present(self.TASK_ITEMS):
            task_elements = self.find_elements(self.TASK_TEXT)
            tasks = [task.text for task in task_elements]
        return tasks
    
    def complete_task(self, task_text: str):
        """Отметка задачи как выполненной"""
        self.logger.info(f"Отметка задачи как выполненной: {task_text}")
        
        task_items = self.find_elements(self.TASK_ITEMS)
        for task_item in task_items:
            text_element = task_item.find_element(*self.TASK_TEXT)
            if text_element.text == task_text:
                checkbox = task_item.find_element(*self.TASK_CHECKBOX)
                if not checkbox.is_selected():
                    checkbox.click()
                break
    
    def delete_task(self, task_text: str):
        """Удаление задачи"""
        self.logger.info(f"Удаление задачи: {task_text}")
        
        task_items = self.find_elements(self.TASK_ITEMS)
        for task_item in task_items:
            text_element = task_item.find_element(*self.TASK_TEXT)
            if text_element.text == task_text:
                delete_button = task_item.find_element(*self.DELETE_TASK_BUTTON)
                delete_button.click()
                break
    
    def edit_task(self, old_text: str, new_text: str):
        """Редактирование задачи"""
        self.logger.info(f"Редактирование задачи: {old_text} -> {new_text}")
        
        task_items = self.find_elements(self.TASK_ITEMS)
        for task_item in task_items:
            text_element = task_item.find_element(*self.TASK_TEXT)
            if text_element.text == old_text:
                edit_button = task_item.find_element(*self.EDIT_TASK_BUTTON)
                edit_button.click()
                
                # Ввод нового текста
                edit_input = task_item.find_element(By.TAG_NAME, "input")
                edit_input.clear()
                edit_input.send_keys(new_text)
                edit_input.send_keys(Keys.ENTER)
                break
    
    def filter_tasks(self, filter_type: str = "all"):
        """Фильтрация задач"""
        self.logger.info(f"Фильтрация задач: {filter_type}")
        
        if filter_type == "active":
            self.click(self.FILTER_ACTIVE)
        elif filter_type == "completed":
            self.click(self.FILTER_COMPLETED)
        else:
            self.click(self.FILTER_ALL)
    
    def clear_completed_tasks(self):
        """Очистка выполненных задач"""
        self.logger.info("Очистка выполненных задач")
        self.click(self.CLEAR_COMPLETED)
    
    def get_task_counter_text(self) -> str:
        """Получение текста счетчика задач"""
        if self.is_element_present(self.TASK_COUNTER):
            return self.get_text(self.TASK_COUNTER)
        return ""
    
    def is_task_completed(self, task_text: str) -> bool:
        """Проверка, выполнена ли задача"""
        task_items = self.find_elements(self.TASK_ITEMS)
        for task_item in task_items:
            text_element = task_item.find_element(*self.TASK_TEXT)
            if text_element.text == task_text:
                checkbox = task_item.find_element(*self.TASK_CHECKBOX)
                return checkbox.is_selected()
        return False
    
    def is_no_tasks_message_displayed(self) -> bool:
        """Проверка отображения сообщения 'Нет задач'"""
        return self.is_element_visible(self.NO_TASKS_MESSAGE)
