"""
Автоматизированные тесты для API задач
"""
import pytest
from api.schemas import Task, TaskList, ErrorResponse


class TestTasksAPI:
    """Тесты для эндпоинтов задач"""
    
    def test_get_all_tasks(self, tasks_api):
        """Тест получения списка задач"""
        response = tasks_api.get_all_tasks()
        assert response.status_code == 200
        
        task_list = TaskList.parse_obj(response.json())
        assert task_list.count >= 0
        assert isinstance(task_list.tasks, list)
    
    def test_create_task_success(self, tasks_api, faker):
        """Тест успешного создания задачи"""
        title = faker.sentence()
        
        response = tasks_api.create_task(title=title)
        assert response.status_code == 201
        
        task = Task.parse_obj(response.json())
        assert task.id > 0
        assert task.title == title
        assert task.completed is False
        
        # Очистка
        tasks_api.delete_task(task.id)
    
    @pytest.mark.parametrize("invalid_title, expected_error", [
        ("", "Поле 'title' обязательно и не может быть пустым"),
        (None, "Требуется JSON тело запроса"),
    ])
    def test_create_task_validation(self, tasks_api, invalid_title, expected_error):
        """Тест валидации при создании задачи"""
        data = {}
        if invalid_title is not None:
            data['title'] = invalid_title
        
        response = tasks_api.create_task(**data)
        assert response.status_code == 400
        
        error = ErrorResponse.parse_obj(response.json())
        assert expected_error in error.error
    
    def test_get_task_by_id(self, tasks_api, test_task):
        """Тест получения задачи по ID"""
        response = tasks_api.get_task(test_task.id)
        assert response.status_code == 200
        
        task = Task.parse_obj(response.json())
        assert task.id == test_task.id
        assert task.title == test_task.title
    
    def test_get_nonexistent_task(self, tasks_api):
        """Тест получения несуществующей задачи"""
        response = tasks_api.get_task(99999)
        assert response.status_code == 404
        
        error = ErrorResponse.parse_obj(response.json())
        assert "не найдена" in error.error.lower()
    
    def test_update_task(self, tasks_api, test_task, faker):
        """Тест обновления задачи"""
        new_title = faker.sentence()
        
        response = tasks_api.update_task(
            task_id=test_task.id,
            title=new_title,
            completed=True
        )
        assert response.status_code == 200
        
        updated_task = Task.parse_obj(response.json())
        assert updated_task.title == new_title
        assert updated_task.completed is True
    
    def test_delete_task(self, tasks_api, faker):
        """Тест удаления задачи"""
        # Создаем задачу для удаления
        title = faker.sentence()
        response = tasks_api.create_task(title=title)
        task_id = response.json()['id']
        
        # Удаляем задачу
        response = tasks_api.delete_task(task_id)
        assert response.status_code == 200
        assert "удалена" in response.json()['message'].lower()
        
        # Проверяем, что задача действительно удалена
        response = tasks_api.get_task(task_id)
        assert response.status_code == 404
    
    @pytest.mark.parametrize("completed_filter", [True, False])
    def test_filter_tasks_by_status(self, tasks_api, completed_filter):
        """Тест фильтрации задач по статусу"""
        response = tasks_api.get_all_tasks(completed=completed_filter)
        assert response.status_code == 200
        
        task_list = TaskList.parse_obj(response.json())
        
        # Проверяем, что все задачи соответствуют фильтру
        for task in task_list.tasks:
            assert task.completed == completed_filter
    
    def test_task_lifecycle(self, tasks_api, faker):
        """Полный жизненный цикл задачи: Create -> Read -> Update -> Delete"""
        # 1. Create
        title1 = faker.sentence()
        response = tasks_api.create_task(title=title1)
        assert response.status_code == 201
        task_id = response.json()['id']
        
        # 2. Read (проверяем создание)
        response = tasks_api.get_task(task_id)
        assert response.status_code == 200
        assert response.json()['title'] == title1
        
        # 3. Update
        title2 = faker.sentence()
        response = tasks_api.update_task(task_id, title2, True)
        assert response.status_code == 200
        assert response.json()['title'] == title2
        assert response.json()['completed'] is True
        
        # 4. Delete
        response = tasks_api.delete_task(task_id)
        assert response.status_code == 200
        
        # 5. Verify deletion
        response = tasks_api.get_task(task_id)
        assert response.status_code == 404
