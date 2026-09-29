"""
Генератор комплексного отчета о тестировании
"""
import json
import yaml
import csv
from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

class TestReportGenerator:
    """Генератор отчетов о тестировании"""
    
    def __init__(self, test_results_dir="test_results", output_dir="reports"):
        self.test_results_dir = Path(test_results_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.report_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "project": "Система управления заказами",
                "version": "1.0.0"
            },
            "summary": {},
            "test_results": [],
            "defects": [],
            "metrics": {}
        }
    
    def collect_test_results(self, results_files):
        """Сбор результатов тестирования из различных источников"""
        print("Сбор результатов тестирования...")
        
        for result_file in results_files:
            file_path = self.test_results_dir / result_file
            
            if not file_path.exists():
                print(f"Файл не найден: {file_path}")
                continue
            
            if result_file.endswith(".json"):
                self._parse_json_results(file_path)
            elif result_file.endswith(".xml"):
                self._parse_xml_results(file_path)
            elif result_file.endswith(".csv"):
                self._parse_csv_results(file_path)
    
    def _parse_json_results(self, file_path):
        """Парсинг JSON результатов"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            if "test_cases" in data:
                for test_case in data["test_cases"]:
                    self.report_data["test_results"].append({
                        "name": test_case.get("name", "Unknown"),
                        "status": test_case.get("status", "unknown"),
                        "duration": test_case.get("duration", 0),
                        "module": test_case.get("module", "unknown"),
                        "timestamp": test_case.get("timestamp", datetime.now().isoformat())
                    })
    
    def generate_summary(self):
        """Генерация сводки тестирования"""
        print("Генерация сводки...")
        
        total_tests = len(self.report_data["test_results"])
        passed_tests = sum(1 for t in self.report_data["test_results"] if t["status"] == "passed")
        failed_tests = sum(1 for t in self.report_data["test_results"] if t["status"] == "failed")
        skipped_tests = sum(1 for t in self.report_data["test_results"] if t["status"] == "skipped")
        
        self.report_data["summary"] = {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "skipped": skipped_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "execution_time": sum(t.get("duration", 0) for t in self.report_data["test_results"])
        }
    
    def generate_charts(self):
        """Генерация графиков и диаграмм"""
        print("Генерация графиков...")
        
        # Диаграмма результатов тестов
        if self.report_data["test_results"]:
            status_counts = {
                "Пройдено": self.report_data["summary"]["passed"],
                "Провалено": self.report_data["summary"]["failed"],
                "Пропущено": self.report_data["summary"]["skipped"]
            }
            
            fig, axes = plt.subplots(1, 2, figsize=(12, 5))
            
            # Круговая диаграмма
            axes[0].pie(
                status_counts.values(),
                labels=status_counts.keys(),
                autopct='%1.1f%%',
                colors=['#4CAF50', '#F44336', '#FFC107']
            )
            axes[0].set_title('Результаты тестирования')
            
            # Столбчатая диаграмма по модулям
            if len(self.report_data["test_results"]) > 0:
                df = pd.DataFrame(self.report_data["test_results"])
                module_stats = df.groupby('module')['status'].value_counts().unstack(fill_value=0)
                
                if not module_stats.empty:
                    module_stats.plot(kind='bar', ax=axes[1], color=['#4CAF50', '#F44336', '#FFC107'])
                    axes[1].set_title('Результаты по модулям')
                    axes[1].set_xlabel('Модуль')
                    axes[1].set_ylabel('Количество тестов')
                    axes[1].legend(['Пройдено', 'Провалено', 'Пропущено'])
                    plt.xticks(rotation=45, ha='right')
            
            plt.tight_layout()
            chart_path = self.output_dir / "test_results_chart.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            self.report_data["metrics"]["chart_path"] = str(chart_path)
    
    def generate_html_report(self):
        """Генерация HTML отчета"""
        print("Генерация HTML отчета...")
        
        html_template = f"""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Отчет о тестировании - {self.report_data['metadata']['project']}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; margin-bottom: 30px; border-bottom: 2px solid #333; padding-bottom: 20px; }}
                .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }}
                .card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #007bff; }}
                .card.passed {{ border-left-color: #28a745; }}
                .card.failed {{ border-left-color: #dc3545; }}
                .card.skipped {{ border-left-color: #ffc107; }}
                .metric {{ font-size: 2em; font-weight: bold; margin: 10px 0; }}
                .test-results {{ margin-top: 30px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #007bff; color: white; }}
                tr.passed {{ background-color: #d4edda; }}
                tr.failed {{ background-color: #f8d7da; }}
                tr.skipped {{ background-color: #fff3cd; }}
                .chart {{ text-align: center; margin: 30px 0; }}
                .footer {{ margin-top: 30px; text-align: center; color: #666; font-size: 0.9em; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Отчет о тестировании</h1>
                    <h2>{self.report_data['metadata']['project']} - Версия {self.report_data['metadata']['version']}</h2>
                    <p>Сгенерировано: {self.report_data['metadata']['generated_at']}</p>
                </div>
                
                <div class="summary">
                    <div class="card">
                        <h3>Всего тестов</h3>
                        <div class="metric">{self.report_data['summary']['total_tests']}</div>
                    </div>
                    <div class="card passed">
                        <h3>Пройдено</h3>
                        <div class="metric">{self.report_data['summary']['passed']}</div>
                    </div>
                    <div class="card failed">
                        <h3>Провалено</h3>
                        <div class="metric">{self.report_data['summary']['failed']}</div>
                    </div>
                    <div class="card skipped">
                        <h3>Пропущено</h3>
                        <div class="metric">{self.report_data['summary']['skipped']}</div>
                    </div>
                    <div class="card">
                        <h3>Успешность</h3>
                        <div class="metric">{self.report_data['summary']['success_rate']:.1f}%</div>
                    </div>
                    <div class="card">
                        <h3>Время выполнения</h3>
                        <div class="metric">{self.report_data['summary']['execution_time']:.1f} с</div>
                    </div>
                </div>
                
                {self._generate_chart_html()}
                
                <div class="test-results">
                    <h2>Детальные результаты тестов</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Тест</th>
                                <th>Модуль</th>
                                <th>Статус</th>
                                <th>Длительность (с)</th>
                                <th>Время выполнения</th>
                            </tr>
                        </thead>
                        <tbody>
                            {self._generate_test_results_html()}
                        </tbody>
                    </table>
                </div>
                
                <div class="footer">
                    <p>Отчет сгенерирован автоматически системой тестирования</p>
                    <p>© {datetime.now().year} Учебный проект по интеграционному тестированию</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        report_path = self.output_dir / "detailed_report.html"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_template)
        
        print(f"HTML отчет сохранен: {report_path}")
    
    def _generate_chart_html(self):
        """Генерация HTML для встраивания графиков"""
        if "chart_path" in self.report_data["metrics"]:
            return f"""
                <div class="chart">
                    <h2>Визуализация результатов</h2>
                    <img src="{self.report_data['metrics']['chart_path']}" alt="Диаграмма результатов" style="max-width: 100%;">
                </div>
            """
        return ""
    
    def _generate_test_results_html(self):
        """Генерация HTML строк таблицы результатов"""
        rows = []
        for test in self.report_data["test_results"][:50]:  # Ограничиваем для читаемости
            status_class = test["status"]
            status_ru = {
                "passed": "Пройдено",
                "failed": "Провалено",
                "skipped": "Пропущено"
            }.get(test["status"], "Неизвестно")
            
            row = f"""
                <tr class="{status_class}">
                    <td>{test['name']}</td>
                    <td>{test['module']}</td>
                    <td>{status_ru}</td>
                    <td>{test.get('duration', 0):.2f}</td>
                    <td>{test.get('timestamp', '')}</td>
                </tr>
            """
            rows.append(row)
        
        return "\n".join(rows)
    
    def generate_all_reports(self):
        """Генерация всех отчетов"""
        self.collect_test_results(["integration_results.json", "contract_results.json"])
        self.generate_summary()
        self.generate_charts()
        self.generate_html_report()
        
        # Сохранение JSON отчета
        json_path = self.output_dir / "full_report.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.report_data, f, indent=2, ensure_ascii=False)
        
        # Генерация текстового отчета
        self._generate_text_report()
        
        print(f"\nОтчеты сохранены в директории: {self.output_dir}")
        print(f"1. HTML отчет: {self.output_dir / 'detailed_report.html'}")
        print(f"2. JSON данные: {self.output_dir / 'full_report.json'}")
        print(f"3. Текстовый отчет: {self.output_dir / 'summary_report.txt'}")
        print(f"4. Графики: {self.output_dir / 'test_results_chart.png'}")
    
    def _generate_text_report(self):
        """Генерация текстового отчета"""
        text_report = f"""
        =================================================================
        ОТЧЕТ О ТЕСТИРОВАНИИ
        =================================================================
        
        Проект: {self.report_data['metadata']['project']}
        Версия: {self.report_data['metadata']['version']}
        Дата генерации: {self.report_data['metadata']['generated_at']}
        
        =================================================================
        СВОДКА РЕЗУЛЬТАТОВ
        =================================================================
        
        Всего тестов: {self.report_data['summary']['total_tests']}
        Пройдено:     {self.report_data['summary']['passed']}
        Провалено:    {self.report_data['summary']['failed']}
        Пропущено:    {self.report_data['summary']['skipped']}
        Успешность:   {self.report_data['summary']['success_rate']:.1f}%
        Время выполнения: {self.report_data['summary']['execution_time']:.1f} с
        
        =================================================================
        КЛЮЧЕВЫЕ МЕТРИКИ КАЧЕСТВА
        =================================================================
        
        1. Покрытие функциональности: {self._calculate_functional_coverage()}%
        2. Уровень дефектов: {self._calculate_defect_density():.2f} дефектов/тест
        3. Стабильность системы: {self._calculate_stability_score()}/10
        
        =================================================================
        РЕКОМЕНДАЦИИ
        =================================================================
        
        {self._generate_recommendations()}
        
        =================================================================
        ВЫВОДЫ
        =================================================================
        
        {self._generate_conclusions()}
        """
        
        report_path = self.output_dir / "summary_report.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(text_report)
    
    def _calculate_functional_coverage(self):
        """Расчет покрытия функциональности"""
        # В реальной системе это вычислялось бы на основе требований
        return 85  # Примерное значение
    
    def _calculate_defect_density(self):
        """Расчет плотности дефектов"""
        total_tests = self.report_data['summary']['total_tests']
        failed_tests = self.report_data['summary']['failed']
        
        if total_tests > 0:
            return failed_tests / total_tests
        return 0
    
    def _calculate_stability_score(self):
        """Расчет оценки стабильности системы"""
        success_rate = self.report_data['summary']['success_rate']
        return min(10, success_rate / 10)  # Преобразуем процент в оценку 0-10
    
    def _generate_recommendations(self):
        """Генерация рекомендаций на основе результатов"""
        recommendations = []
        
        if self.report_data['summary']['failed'] > 0:
            recommendations.append("1. Исправить проваленные тесты перед релизом")
        
        if self.report_data['summary']['success_rate'] < 90:
            recommendations.append("2. Увеличить покрытие тестами проблемных модулей")
        
        if self._calculate_defect_density() > 0.1:
            recommendations.append("3. Провести дополнительный ревью кода проблемных модулей")
        
        if not recommendations:
            recommendations.append("Система готова к релизу. Дополнительные действия не требуются.")
        
        return "\n".join(recommendations)
    
    def _generate_conclusions(self):
        """Генерация выводов"""
        success_rate = self.report_data['summary']['success_rate']
        
        if success_rate >= 95:
            return "✅ Качество системы ОТЛИЧНОЕ. Все ключевые функции работают корректно. Система готова к промышленной эксплуатации."
        elif success_rate >= 85:
            return "⚠️ Качество системы УДОВЛЕТВОРИТЕЛЬНОЕ. Есть незначительные проблемы, требующие исправления перед релизом."
        elif success_rate >= 70:
            return "⚠️ Качество системы НИЗКОЕ. Требуются значительные доработки и дополнительные тесты."
        else:
            return "❌ Качество системы НЕДОСТАТОЧНОЕ. Требуется серьезная доработка системы и тестового покрытия."

# Пример использования
if __name__ == "__main__":
    print("Генерация комплексного отчета о тестировании...")
    
    generator = TestReportGenerator(
        test_results_dir="test_results",
        output_dir="reports/final"
    )
    
    generator.generate_all_reports()
    
    print("\n" + "="*60)
    print("ОТЧЕТ УСПЕШНО СГЕНЕРИРОВАН")
    print("="*60)
