"""
通知规则管理器 - 负责决定何时发送哪种类型的通知
"""
import logging
from typing import List, Dict, Any, Optional
from .types.enums import NotificationType, NotificationImportance, ProviderType

logger = logging.getLogger(__name__)


class NotificationRulesManager:
    """通知规则管理器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化通知规则管理器
        
        Args:
            config: 规则配置
        """
        self.config = config or {}
        self._load_default_rules()
    
    def _load_default_rules(self):
        """加载默认规则"""
        self.rules = {
            # 应用内通知规则 - 所有通知都发送
            ProviderType.IN_APP: {
                "enabled": True,
                "conditions": {
                    "all_types": True,  # 所有类型都发送
                    "all_importance": True  # 所有重要性都发送
                }
            },
            
            # 短信通知规则 - 仅最严重的逾期预警
            ProviderType.SMS: {
                "enabled": True,
                "conditions": {
                    "importance": [NotificationImportance.HIGH],  # 仅最高重要性
                    "types": [NotificationType.PROJECT],  # 仅项目相关
                    "required_keywords": ["严重逾期", "提交预警"],  # 必须包含严重预警关键词
                    "min_days_threshold": 3  # 连续3天以上无提交才发短信
                }
            },
            
            # 飞书通知规则 - 高重要性或包含预警关键词
            ProviderType.FEISHU: {
                "enabled": True,
                "conditions": {
                    "importance": [NotificationImportance.HIGH],  # 高重要性
                    "keywords": ["预警", "Warning", "严重"],  # 或包含预警关键词
                    "min_importance_for_keywords": NotificationImportance.NORMAL  # 包含关键词时的最低重要性
                }
            }
        }
        
        # 合并用户配置
        if self.config.get('rules'):
            self.rules.update(self.config['rules'])
    
    def should_send_with_provider(
        self, 
        provider_type: ProviderType, 
        notification_type: NotificationType,
        importance: NotificationImportance,
        title: str = "",
        content: str = ""
    ) -> bool:
        """
        判断是否应该使用指定提供商发送通知
        
        Args:
            provider_type: 提供商类型
            notification_type: 通知类型
            importance: 重要性级别
            title: 通知标题
            content: 通知内容
            
        Returns:
            是否应该发送
        """
        if provider_type not in self.rules:
            return False
        
        rule = self.rules[provider_type]
        
        # 检查是否启用
        if not rule.get("enabled", True):
            return False
        
        conditions = rule.get("conditions", {})
        
        # 应用内通知 - 发送所有通知
        if provider_type == ProviderType.IN_APP:
            return conditions.get("all_types", True) and conditions.get("all_importance", True)
        
        # 短信通知规则 - 仅最严重的项目逾期预警
        elif provider_type == ProviderType.SMS:
            # 必须是高重要性
            if importance != NotificationImportance.HIGH:
                return False
            
            # 必须是项目类型
            if notification_type != NotificationType.PROJECT:
                return False
            
            # 检查必需关键词
            if "required_keywords" in conditions:
                required_keywords = conditions["required_keywords"]
                has_all_keywords = all(
                    any(keyword in title or keyword in content for keyword in [req_keyword])
                    for req_keyword in required_keywords
                )
                if not has_all_keywords:
                    return False
            
            # 检查天数阈值（如果提供了额外参数）
            days_threshold = conditions.get("min_days_threshold", 0)
            if days_threshold > 0:
                # 这里可以从content中提取天数信息，或者通过额外参数传入
                # 简化处理：如果内容包含天数信息
                import re
                days_match = re.search(r'(\d+)\s*天', content)
                if days_match:
                    days = int(days_match.group(1))
                    if days < days_threshold:
                        return False
            
            return True
        
        # 飞书通知规则
        elif provider_type == ProviderType.FEISHU:
            # 高重要性直接发送
            if importance == NotificationImportance.HIGH:
                return True
            
            # 检查关键词
            if "keywords" in conditions:
                keywords = conditions["keywords"]
                has_keyword = any(keyword in title or keyword in content for keyword in keywords)
                
                if has_keyword:
                    # 有关键词，检查是否满足最低重要性要求
                    min_importance = conditions.get("min_importance_for_keywords", NotificationImportance.NORMAL)
                    return self._compare_importance(importance, min_importance)
            
            return False
        
        # 其他提供商的默认规则
        return False
    
    def get_enabled_providers(
        self,
        notification_type: NotificationType,
        importance: NotificationImportance,
        title: str = "",
        content: str = ""
    ) -> List[ProviderType]:
        """
        获取应该启用的提供商列表
        
        Args:
            notification_type: 通知类型
            importance: 重要性级别
            title: 通知标题
            content: 通知内容
            
        Returns:
            应该启用的提供商列表
        """
        enabled_providers = []
        
        for provider_type in ProviderType:
            if self.should_send_with_provider(provider_type, notification_type, importance, title, content):
                enabled_providers.append(provider_type)
        
        return enabled_providers
    
    def _compare_importance(self, importance1: NotificationImportance, importance2: NotificationImportance) -> bool:
        """
        比较重要性级别（importance1 >= importance2）
        
        Args:
            importance1: 重要性1
            importance2: 重要性2
            
        Returns:
            importance1 是否大于等于 importance2
        """
        importance_levels = {
            NotificationImportance.LOW: 1,
            NotificationImportance.NORMAL: 2,
            NotificationImportance.HIGH: 3
        }
        
        return importance_levels.get(importance1, 0) >= importance_levels.get(importance2, 0)
    
    def update_rule(self, provider_type: ProviderType, rule_config: Dict[str, Any]):
        """
        更新指定提供商的规则
        
        Args:
            provider_type: 提供商类型
            rule_config: 规则配置
        """
        if provider_type in self.rules:
            self.rules[provider_type].update(rule_config)
        else:
            self.rules[provider_type] = rule_config
        
        logger.info(f"已更新 {provider_type.value} 的通知规则")
    
    def get_rule(self, provider_type: ProviderType) -> Dict[str, Any]:
        """
        获取指定提供商的规则
        
        Args:
            provider_type: 提供商类型
            
        Returns:
            规则配置
        """
        return self.rules.get(provider_type, {})
    
    def get_all_rules(self) -> Dict[ProviderType, Dict[str, Any]]:
        """
        获取所有规则
        
        Returns:
            所有规则配置
        """
        return self.rules.copy()
