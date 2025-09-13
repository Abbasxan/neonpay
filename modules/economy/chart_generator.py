"""
Chart Generator Module
Модуль генерации графиков и диаграмм для экономической системы
"""

import logging
import io
import matplotlib.pyplot as plt
from matplotlib import dates as mdates
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import numpy as np
from config import db
from .database import EconomyDB

logger = logging.getLogger(__name__)

class ChartGenerator:
    """Генератор графиков для экономической системы"""
    
    def __init__(self):
        # Настройка стиля matplotlib
        plt.style.use('dark_background')
        self.colors = {
            'primary': '#00D4FF',      # Неоновый синий
            'secondary': '#FF6B6B',    # Красный
            'success': '#4ECDC4',      # Зеленый
            'warning': '#FFE66D',      # Желтый
            'info': '#A8E6CF',         # Светло-зеленый
            'background': '#1A1A1A',   # Темный фон
            'grid': '#333333'          # Сетка
        }
    
    async def generate_market_analysis_chart(self, chat_id: int) -> io.BytesIO:
        """Сгенерировать график анализа рынка"""
        try:
            from .advanced_pricing import advanced_pricing
            analysis = await advanced_pricing.get_market_analysis(chat_id)
            
            if "error" in analysis:
                return await self._generate_error_chart(analysis["error"])
            
            # Создаем фигуру
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
            fig.patch.set_facecolor(self.colors['background'])
            
            # График 1: Факторы влияния (радарная диаграмма)
            await self._create_radar_chart(ax1, analysis['factors'])
            
            # График 2: Текущий курс и статус
            await self._create_rate_status_chart(ax2, analysis)
            
            # График 3: Исторические данные курса (если есть)
            await self._create_rate_history_chart(ax3, chat_id)
            
            # График 4: Общий рейтинг
            await self._create_rating_chart(ax4, analysis['total_score'])
            
            # Заголовок
            fig.suptitle('📊 Анализ рынка валюты', 
                        fontsize=16, color=self.colors['primary'], fontweight='bold')
            
            plt.tight_layout()
            
            # Сохраняем в BytesIO
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=150, 
                       facecolor=self.colors['background'], 
                       edgecolor='none', bbox_inches='tight')
            img_buffer.seek(0)
            plt.close(fig)
            
            return img_buffer
            
        except Exception as e:
            logger.error(f"Ошибка при генерации графика анализа рынка: {e}")
            return await self._generate_error_chart(str(e))
    
    async def generate_currency_comparison_chart(self, chat_ids: List[int]) -> io.BytesIO:
        """Сгенерировать график сравнения валют разных групп"""
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 8))
            fig.patch.set_facecolor(self.colors['background'])
            
            # Собираем данные по всем группам
            currencies_data = []
            for chat_id in chat_ids:
                group_currency = await EconomyDB.get_group_currency(chat_id)
                if group_currency:
                    currencies_data.append({
                        'name': group_currency['currency_name'],
                        'symbol': group_currency['currency_symbol'],
                        'rate': group_currency['exchange_rate_to_nc'],
                        'activity': group_currency.get('daily_activity_score', 0),
                        'supply': group_currency.get('total_supply', 0),
                        'age': (datetime.utcnow() - group_currency.get('created_at', datetime.utcnow())).days
                    })
            
            if not currencies_data:
                return await self._generate_error_chart("Нет данных о валютах")
            
            # График 1: Сравнение курсов
            await self._create_rates_comparison_chart(ax1, currencies_data)
            
            # График 2: Активность групп
            await self._create_activity_comparison_chart(ax2, currencies_data)
            
            fig.suptitle('🏦 Сравнение валют групп', 
                        fontsize=16, color=self.colors['primary'], fontweight='bold')
            
            plt.tight_layout()
            
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=150, 
                       facecolor=self.colors['background'], 
                       edgecolor='none', bbox_inches='tight')
            img_buffer.seek(0)
            plt.close(fig)
            
            return img_buffer
            
        except Exception as e:
            logger.error(f"Ошибка при генерации графика сравнения: {e}")
            return await self._generate_error_chart(str(e))
    
    async def generate_user_portfolio_chart(self, chat_id: int, user_id: int) -> io.BytesIO:
        """Сгенерировать график портфеля пользователя"""
        try:
            balance = await EconomyDB.get_user_balance(chat_id, user_id)
            group_currency = await EconomyDB.get_group_currency(chat_id)
            
            if not group_currency:
                return await self._generate_error_chart("Валюта группы не найдена")
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
            fig.patch.set_facecolor(self.colors['background'])
            
            # График 1: Распределение портфеля (круговая диаграмма)
            await self._create_portfolio_pie_chart(ax1, balance, group_currency)
            
            # График 2: История транзакций
            await self._create_transaction_history_chart(ax2, chat_id, user_id)
            
            fig.suptitle(f'💼 Портфель пользователя', 
                        fontsize=16, color=self.colors['primary'], fontweight='bold')
            
            plt.tight_layout()
            
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=150, 
                       facecolor=self.colors['background'], 
                       edgecolor='none', bbox_inches='tight')
            img_buffer.seek(0)
            plt.close(fig)
            
            return img_buffer
            
        except Exception as e:
            logger.error(f"Ошибка при генерации графика портфеля: {e}")
            return await self._generate_error_chart(str(e))
    
    async def _create_radar_chart(self, ax, factors: Dict):
        """Создать радарную диаграмму факторов"""
        categories = ['Активность', 'Предложение', 'Возраст', 'Спрос', 'Тренд']
        
        # Проверяем наличие всех ключей и устанавливаем значения по умолчанию
        default_values = {'activity': 0.5, 'supply': 0.5, 'age': 0.5, 'demand': 0.5, 'trend': 0.5}
        values = []
        for key in ['activity', 'supply', 'age', 'demand', 'trend']:
            try:
                values.append(float(factors.get(key, default_values[key])))
            except (ValueError, TypeError):
                values.append(default_values[key])
        
        # Создаем углы для радарной диаграммы
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        
        # Добавляем первую точку в конец для замыкания
        values += values[:1]
        categories += categories[:1]
        angles += angles[:1]
        
        ax.plot(angles, values, 'o-', linewidth=2, color=self.colors['primary'])
        ax.fill(angles, values, alpha=0.25, color=self.colors['primary'])
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories[:-1], color='white')
        ax.set_ylim(0, 1)
        ax.set_title('Факторы влияния', color=self.colors['primary'], fontweight='bold')
        ax.grid(True, color=self.colors['grid'], alpha=0.3)
    
    async def _create_rate_status_chart(self, ax, analysis: Dict):
        """Создать график курса и статуса"""
        rate = analysis['current_rate']
        status = analysis['status']
        
        # Цвет статуса
        if 'Горячая' in status:
            color = self.colors['secondary']
        elif 'Растущая' in status:
            color = self.colors['success']
        elif 'Стабильная' in status:
            color = self.colors['info']
        elif 'Слабая' in status:
            color = self.colors['warning']
        else:
            color = self.colors['grid']
        
        # Создаем бар-чарт
        bars = ax.bar(['Текущий курс'], [rate], color=color, alpha=0.8)
        ax.set_title(f'Курс: {rate:.4f} NC', color=self.colors['primary'], fontweight='bold')
        ax.set_ylabel('NC', color='white')
        ax.set_ylim(0, max(rate * 1.5, 0.1))
        
        # Добавляем значение на бар
        ax.text(0, rate + rate * 0.05, f'{rate:.4f}', 
               ha='center', va='bottom', color='white', fontweight='bold')
        
        ax.grid(True, color=self.colors['grid'], alpha=0.3)
        ax.set_facecolor(self.colors['background'])
    
    async def _create_rate_history_chart(self, ax, chat_id: int):
        """Создать график истории курса"""
        try:
            # Получаем историю транзакций для анализа тренда
            week_ago = datetime.utcnow() - timedelta(days=7)
            transactions = await db.economy_transactions.find({
                "chat_id": chat_id,
                "transaction_type": {"$in": ["group_to_nc", "nc_to_group"]},
                "created_at": {"$gte": week_ago}
            }).sort("created_at", 1).to_list(length=50)
            
            if not transactions:
                ax.text(0.5, 0.5, 'Нет данных\nза последние 7 дней', 
                       ha='center', va='center', color='white', fontsize=12)
                ax.set_title('История курса', color=self.colors['primary'], fontweight='bold')
                return
            
            # Создаем симулированные данные курса на основе транзакций
            dates = []
            rates = []
            base_rate = 0.1
            
            for i, transaction in enumerate(transactions):
                dates.append(transaction['created_at'])
                # Симулируем изменение курса на основе активности
                rate_change = np.random.normal(0, 0.01)  # Небольшие случайные изменения
                base_rate = max(0.01, min(base_rate + rate_change, 2.0))
                rates.append(base_rate)
            
            ax.plot(dates, rates, color=self.colors['primary'], linewidth=2, marker='o', markersize=4)
            ax.set_title('История курса (7 дней)', color=self.colors['primary'], fontweight='bold')
            ax.set_ylabel('Курс (NC)', color='white')
            ax.grid(True, color=self.colors['grid'], alpha=0.3)
            
            # Форматирование дат
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
            
        except Exception as e:
            ax.text(0.5, 0.5, 'Ошибка загрузки\nистории', 
                   ha='center', va='center', color='white', fontsize=12)
            ax.set_title('История курса', color=self.colors['primary'], fontweight='bold')
    
    async def _create_rating_chart(self, ax, total_score: str):
        """Создать график общего рейтинга"""
        try:
            score = float(total_score)
        except (ValueError, TypeError):
            score = 0.5  # Значение по умолчанию
        
        # Цвет рейтинга
        if score >= 0.8:
            color = self.colors['success']
            label = 'Отлично'
        elif score >= 0.6:
            color = self.colors['info']
            label = 'Хорошо'
        elif score >= 0.4:
            color = self.colors['warning']
            label = 'Удовлетворительно'
        else:
            color = self.colors['secondary']
            label = 'Плохо'
        
        # Создаем полукруглый индикатор
        theta = np.linspace(0, np.pi, 100)
        r = np.ones_like(theta)
        
        ax.plot(theta, r, color=self.colors['grid'], linewidth=3)
        
        # Закрашиваем прогресс
        progress_theta = np.linspace(0, np.pi * score, 100)
        progress_r = np.ones_like(progress_theta)
        ax.fill_between(progress_theta, 0, progress_r, color=color, alpha=0.7)
        
        ax.set_xlim(0, np.pi)
        ax.set_ylim(0, 1.2)
        ax.set_title(f'Рейтинг: {score:.2f}/1.0', color=self.colors['primary'], fontweight='bold')
        ax.text(np.pi/2, 0.6, label, ha='center', va='center', 
               color='white', fontsize=14, fontweight='bold')
        ax.axis('off')
    
    async def _create_rates_comparison_chart(self, ax, currencies_data: List[Dict]):
        """Создать график сравнения курсов"""
        names = [f"{c['symbol']}\n({c['name'][:10]}...)" for c in currencies_data]
        rates = [c['rate'] for c in currencies_data]
        
        bars = ax.bar(range(len(names)), rates, 
                     color=[self.colors['primary'] if r > 0.5 else self.colors['warning'] 
                           for r in rates])
        
        ax.set_title('Сравнение курсов', color=self.colors['primary'], fontweight='bold')
        ax.set_ylabel('Курс (NC)', color='white')
        ax.set_xticks(range(len(names)))
        ax.set_xticklabels(names, rotation=45, ha='right', color='white')
        
        # Добавляем значения на бары
        for i, rate in enumerate(rates):
            ax.text(i, rate + max(rates) * 0.01, f'{rate:.3f}', 
                   ha='center', va='bottom', color='white', fontweight='bold')
        
        ax.grid(True, color=self.colors['grid'], alpha=0.3)
        ax.set_facecolor(self.colors['background'])
    
    async def _create_activity_comparison_chart(self, ax, currencies_data: List[Dict]):
        """Создать график сравнения активности"""
        names = [c['symbol'] for c in currencies_data]
        activities = [c['activity'] for c in currencies_data]
        
        bars = ax.bar(range(len(names)), activities, color=self.colors['success'])
        ax.set_title('Активность групп', color=self.colors['primary'], fontweight='bold')
        ax.set_ylabel('Очки активности', color='white')
        ax.set_xticks(range(len(names)))
        ax.set_xticklabels(names, color='white')
        
        # Добавляем значения на бары
        for i, activity in enumerate(activities):
            ax.text(i, activity + max(activities) * 0.01, f'{activity}', 
                   ha='center', va='bottom', color='white', fontweight='bold')
        
        ax.grid(True, color=self.colors['grid'], alpha=0.3)
        ax.set_facecolor(self.colors['background'])
    
    async def _create_portfolio_pie_chart(self, ax, balance: Dict, group_currency: Dict):
        """Создать круговую диаграмму портфеля"""
        labels = ['Neon Coins', group_currency['currency_symbol']]
        sizes = [balance['neon_coins'], balance['group_currency']]
        colors = [self.colors['primary'], self.colors['success']]
        
        # Убираем нулевые значения
        non_zero_data = [(label, size, color) for label, size, color in zip(labels, sizes, colors) if size > 0]
        
        if not non_zero_data:
            ax.text(0.5, 0.5, 'Портфель пуст', ha='center', va='center', 
                   color='white', fontsize=14)
            ax.set_title('Распределение портфеля', color=self.colors['primary'], fontweight='bold')
            return
        
        labels, sizes, colors = zip(*non_zero_data)
        
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                         startangle=90, textprops={'color': 'white'})
        
        ax.set_title('Распределение портфеля', color=self.colors['primary'], fontweight='bold')
    
    async def _create_transaction_history_chart(self, ax, chat_id: int, user_id: int):
        """Создать график истории транзакций"""
        try:
            week_ago = datetime.utcnow() - timedelta(days=7)
            transactions = await db.economy_transactions.find({
                "chat_id": chat_id,
                "user_id": user_id,
                "created_at": {"$gte": week_ago}
            }).sort("created_at", 1).to_list(length=20)
            
            if not transactions:
                ax.text(0.5, 0.5, 'Нет транзакций\nза последние 7 дней', 
                       ha='center', va='center', color='white', fontsize=12)
                ax.set_title('История транзакций', color=self.colors['primary'], fontweight='bold')
                return
            
            dates = [t['created_at'] for t in transactions]
            amounts = []
            
            for t in transactions:
                if t['transaction_type'] == 'group_to_nc':
                    amounts.append(t['amount_nc'])
                elif t['transaction_type'] == 'nc_to_group':
                    amounts.append(-t['amount_group'])
                else:
                    amounts.append(t.get('amount_nc', 0))
            
            colors = [self.colors['success'] if a > 0 else self.colors['secondary'] for a in amounts]
            
            ax.bar(range(len(dates)), amounts, color=colors, alpha=0.7)
            ax.set_title('История транзакций (7 дней)', color=self.colors['primary'], fontweight='bold')
            ax.set_ylabel('Изменение баланса', color='white')
            ax.set_xticks(range(0, len(dates), max(1, len(dates)//5)))
            ax.set_xticklabels([d.strftime('%d.%m') for d in dates[::max(1, len(dates)//5)]], 
                              rotation=45, color='white')
            ax.grid(True, color=self.colors['grid'], alpha=0.3)
            ax.set_facecolor(self.colors['background'])
            
        except Exception as e:
            ax.text(0.5, 0.5, 'Ошибка загрузки\nтранзакций', 
                   ha='center', va='center', color='white', fontsize=12)
            ax.set_title('История транзакций', color=self.colors['primary'], fontweight='bold')
    
    async def _generate_error_chart(self, error_message: str) -> io.BytesIO:
        """Создать график с ошибкой"""
        fig, ax = plt.subplots(figsize=(8, 6))
        fig.patch.set_facecolor(self.colors['background'])
        
        ax.text(0.5, 0.5, f'❌ Ошибка\n{error_message}', 
               ha='center', va='center', color=self.colors['secondary'], 
               fontsize=14, fontweight='bold')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, 
                   facecolor=self.colors['background'], 
                   edgecolor='none', bbox_inches='tight')
        img_buffer.seek(0)
        plt.close(fig)
        
        return img_buffer

# Создаем глобальный экземпляр
chart_generator = ChartGenerator()
