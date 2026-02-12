"""
Servicio para gestión de estadísticas y dashboards.
Centraliza toda la lógica de cálculo de KPIs y métricas.
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from backend.app.models import WorkOrder, Sede, Provider, Payment, User, db
from backend.app.services import BaseService, CacheService
import logging

logger = logging.getLogger(__name__)

class StatsService(BaseService):
    """Servicio para cálculo de estadísticas y métricas"""
    
    def get_dashboard_stats(self, user: User = None) -> Dict:
        """Obtener estadísticas principales para el dashboard"""
        cache_key = "dashboard_stats_main"
        cached_stats = CacheService.get(cache_key)
        
        if cached_stats is not None:
            return cached_stats
        
        try:
            stats = {
                'total_sedes': self._get_total_sedes(),
                'total_ordenes': self._get_total_ordenes(),
                'total_ventas': self._get_total_ventas(),
                'utilidad': self._get_utilidad_total(),
                'ordenes_pendientes': self._get_ordenes_pendientes(),
                'ordenes_completadas': self._get_ordenes_completadas(),
                'system_stats': self._get_system_stats()
            }
            
            # Cache por 5 minutos
            CacheService.set(cache_key, stats, ttl=300)
            return stats
            
        except Exception as e:
            logger.error(f"Error getting dashboard stats: {e}")
            return self._get_empty_stats()
    
    def get_sede_performance(self, limit: int = None) -> List[Dict]:
        """Obtener performance detallado por sede"""
        cache_key = f"sede_performance_{limit or 'all'}"
        cached_performance = CacheService.get(cache_key)
        
        if cached_performance is not None:
            return cached_performance
        
        try:
            # Subconsulta para contar órdenes por sede
            order_counts = db.session.query(
                WorkOrder.sede_id,
                func.count(WorkOrder.id).label('total_ordenes'),
                func.count(func.nullif(WorkOrder.status == 'finalizada', False)).label('ordenes_completadas'),
                func.sum(func.coalesce(WorkOrder.sale_price, 0)).label('total_ventas'),
                func.sum(func.coalesce(WorkOrder.total_amount, 0)).label('total_costos')
            ).group_by(WorkOrder.sede_id).subquery()
            
            # Consulta principal
            query = db.session.query(
                Sede.id,
                Sede.name,
                Sede.city,
                Sede.department,
                func.coalesce(order_counts.c.total_ordenes, 0).label('total_ordenes'),
                func.coalesce(order_counts.c.ordenes_completadas, 0).label('ordenes_completadas'),
                func.coalesce(order_counts.c.total_ventas, 0).label('total_ventas'),
                func.coalesce(order_counts.c.total_costos, 0).label('total_costos')
            ).outerjoin(
                order_counts, Sede.id == order_counts.c.sede_id
            ).filter(
                Sede.is_active == True
            ).order_by(
                desc(func.coalesce(order_counts.c.total_ventas, 0))
            )
            
            if limit:
                query = query.limit(limit)
            
            results = query.all()
            
            performance_data = []
            for result in results:
                utilidad = result.total_ventas - result.total_costos
                margen = (utilidad / result.total_ventas * 100) if result.total_ventas > 0 else 0
                tasa_completadas = (result.ordenes_completadas / result.total_ordenes * 100) if result.total_ordenes > 0 else 0
                
                performance_data.append({
                    'sede_id': result.id,
                    'sede_name': result.name,
                    'city': result.city,
                    'department': result.department,
                    'total_ordenes': result.total_ordenes,
                    'ordenes_completadas': result.ordenes_completadas,
                    'total_ventas': float(result.total_ventas),
                    'total_costos': float(result.total_costos),
                    'utilidad': float(utilidad),
                    'margen': round(margen, 2),
                    'tasa_completadas': round(tasa_completadas, 2)
                })
            
            # Cache por 10 minutos
            CacheService.set(cache_key, performance_data, ttl=600)
            return performance_data
            
        except Exception as e:
            logger.error(f"Error getting sede performance: {e}")
            return []
    
    def get_monthly_trends(self, months: int = 12) -> Dict:
        """Obtener tendencias mensuales"""
        cache_key = f"monthly_trends_{months}"
        cached_trends = CacheService.get(cache_key)
        
        if cached_trends is not None:
            return cached_trends
        
        try:
            end_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            start_date = end_date - timedelta(days=30 * months)
            
            # Datos por mes
            monthly_data = db.session.query(
                func.date_trunc('month', WorkOrder.created_at).label('month'),
                func.count(WorkOrder.id).label('ordenes'),
                func.sum(func.coalesce(WorkOrder.sale_price, 0)).label('ventas'),
                func.sum(func.coalesce(WorkOrder.total_amount, 0)).label('costos')
            ).filter(
                WorkOrder.created_at >= start_date,
                WorkOrder.created_at < end_date + timedelta(days=32)
            ).group_by(
                func.date_trunc('month', WorkOrder.created_at)
            ).order_by('month').all()
            
            trends = {
                'months': [],
                'ordenes': [],
                'ventas': [],
                'utilidad': []
            }
            
            for data in monthly_data:
                month_name = data.month.strftime('%b %Y')
                utilidad = (data.ventas or 0) - (data.costos or 0)
                
                trends['months'].append(month_name)
                trends['ordenes'].append(data.ordenes)
                trends['ventas'].append(float(data.ventas or 0))
                trends['utilidad'].append(float(utilidad))
            
            # Cache por 1 hora
            CacheService.set(cache_key, trends, ttl=3600)
            return trends
            
        except Exception as e:
            logger.error(f"Error getting monthly trends: {e}")
            return {'months': [], 'ordenes': [], 'ventas': [], 'utilidad': []}
    
    def get_lens_distribution(self) -> Dict:
        """Obtener distribución de tipos de lentes"""
        cache_key = "lens_distribution"
        cached_distribution = CacheService.get(cache_key)
        
        if cached_distribution is not None:
            return cached_distribution
        
        try:
            lens_data = db.session.query(
                WorkOrder.lens_class,
                func.count(WorkOrder.id).label('count')
            ).filter(
                WorkOrder.lens_class.isnot(None),
                WorkOrder.lens_class != ''
            ).group_by(WorkOrder.lens_class).all()
            
            distribution = {
                'labels': [],
                'data': [],
                'total': 0
            }
            
            for item in lens_data:
                distribution['labels'].append(item.lens_class or 'Sin especificar')
                distribution['data'].append(item.count)
                distribution['total'] += item.count
            
            # Cache por 30 minutos
            CacheService.set(cache_key, distribution, ttl=1800)
            return distribution
            
        except Exception as e:
            logger.error(f"Error getting lens distribution: {e}")
            return {'labels': [], 'data': [], 'total': 0}
    
    def get_provider_performance(self) -> List[Dict]:
        """Obtener performance de proveedores"""
        cache_key = "provider_performance"
        cached_performance = CacheService.get(cache_key)
        
        if cached_performance is not None:
            return cached_performance
        
        try:
            provider_data = db.session.query(
                Provider.id,
                Provider.razon_social,
                func.count(WorkOrder.id).label('total_ordenes'),
                func.count(func.nullif(WorkOrder.status == 'finalizada', False)).label('completadas'),
                func.avg(
                    func.extract('epoch', WorkOrder.delivery_deadline - WorkOrder.accepted_at) / 86400
                ).label('avg_delivery_days'),
                func.sum(func.coalesce(WorkOrder.total_amount, 0)).label('total_facturado')
            ).outerjoin(
                WorkOrder, Provider.id == WorkOrder.provider_id
            ).group_by(
                Provider.id, Provider.razon_social
            ).having(
                func.count(WorkOrder.id) > 0
            ).order_by(
                desc(func.count(WorkOrder.id))
            ).all()
            
            performance_data = []
            for data in provider_data:
                tasa_completadas = (data.completadas / data.total_ordenes * 100) if data.total_ordenes > 0 else 0
                
                performance_data.append({
                    'provider_id': data.id,
                    'razon_social': data.razon_social,
                    'total_ordenes': data.total_ordenes,
                    'completadas': data.completadas,
                    'tasa_completadas': round(tasa_completadas, 2),
                    'avg_delivery_days': round(float(data.avg_delivery_days or 0), 1),
                    'total_facturado': float(data.total_facturado or 0)
                })
            
            # Cache por 15 minutos
            CacheService.set(cache_key, performance_data, ttl=900)
            return performance_data
            
        except Exception as e:
            logger.error(f"Error getting provider performance: {e}")
            return []
    
    def _get_total_sedes(self) -> int:
        """Obtener total de sedes activas"""
        return Sede.query.filter_by(is_active=True).count()
    
    def _get_total_ordenes(self) -> int:
        """Obtener total de órdenes"""
        return WorkOrder.query.count()
    
    def _get_total_ventas(self) -> float:
        """Obtener total de ventas"""
        result = db.session.query(
            func.sum(func.coalesce(WorkOrder.sale_price, 0))
        ).scalar()
        return float(result or 0)
    
    def _get_utilidad_total(self) -> float:
        """Calcular utilidad total"""
        ventas = self._get_total_ventas()
        
        costos_result = db.session.query(
            func.sum(func.coalesce(WorkOrder.total_amount, 0))
        ).scalar()
        costos = float(costos_result or 0)
        
        return ventas - costos
    
    def _get_ordenes_pendientes(self) -> int:
        """Obtener órdenes pendientes"""
        return WorkOrder.query.filter(
            WorkOrder.status.in_(['pendiente_envio', 'enviada', 'aceptada', 'en_proceso'])
        ).count()
    
    def _get_ordenes_completadas(self) -> int:
        """Obtener órdenes completadas"""
        return WorkOrder.query.filter_by(status='finalizada').count()
    
    def _get_system_stats(self) -> Dict:
        """Obtener estadísticas del sistema"""
        return {
            'total_sedes': self._get_total_sedes(),
            'total_sedes_active': self._get_total_sedes(),
            'total_providers': Provider.query.count(),
            'total_users': User.query.filter_by(is_active=True).count()
        }
    
    def _get_empty_stats(self) -> Dict:
        """Obtener estadísticas vacías en caso de error"""
        return {
            'total_sedes': 0,
            'total_ordenes': 0,
            'total_ventas': 0.0,
            'utilidad': 0.0,
            'ordenes_pendientes': 0,
            'ordenes_completadas': 0,
            'system_stats': {
                'total_sedes': 0,
                'total_sedes_active': 0,
                'total_providers': 0,
                'total_users': 0
            }
        }
    
    def clear_all_stats_cache(self):
        """Limpiar todo el cache de estadísticas"""
        cache_keys = [
            "dashboard_stats_main",
            "sede_performance_all",
            "sede_performance_5",
            "sede_performance_10",
            "monthly_trends_12",
            "lens_distribution",
            "provider_performance"
        ]
        
        for key in cache_keys:
            CacheService.delete(key)