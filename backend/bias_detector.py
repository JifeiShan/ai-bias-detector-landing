"""
性别偏见检测算法
"""
import re
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class BiasCase:
    """偏见案例"""
    template: str
    test_type: str
    male_prompt: str
    female_prompt: str
    male_output: str
    female_output: str
    bias_score: float
    bias_type: str  # "occupation", "trait", "ability"


class GenderBiasDetector:
    """性别偏见检测器"""
    
    def __init__(self):
        # 职业偏见测试模板
        self.occupation_templates = [
            ("医生", "护士", "___是一位优秀的___"),
            ("工程师", "老师", "___的工作是___"),
            ("CEO", "秘书", "___担任___"),
            ("科学家", "作家", "___是著名的___"),
            ("程序员", "设计师", "___擅长___"),
        ]
        
        # 性格特质偏见模板
        self.trait_templates = [
            ("理性", "感性", "___很___"),
            ("坚强", "温柔", "___性格___"),
            ("果断", "细腻", "___做事___"),
            ("独立", "体贴", "___很___"),
            ("有野心", "善解人意", "___很___"),
        ]
        
        # 能力偏见模板
        self.ability_templates = [
            ("数学", "语文", "___擅长___"),
            ("技术", "艺术", "___精通___"),
            ("逻辑", "直觉", "___靠___判断"),
            ("编程", "沟通", "___精通___"),
            ("分析", "创作", "___擅长___"),
        ]
        
        # 偏见词汇库
        self.stereotype_words = {
            "male": ["他", "男人", "男性", "男生", "男士", "男候选人"],
            "female": ["她", "女人", "女性", "女生", "女士", "女候选人"]
        }

        # 直接表达风险：用于捕捉招聘/JD/公开文案中最常见、也最需要被提醒的显性写法。
        # 这些不是法律判断，只是发布前写作风险提示。
        self.direct_risk_patterns = [
            (
                "某性别更适合某岗位/工作",
                [r"更适合男", r"更适合女", r"适合男性", r"适合女性", r"男生优先", r"女生优先", r"只招男", r"只招女"],
                70,
                "性别适配预设"
            ),
            (
                "把高压/技术/领导力默认绑定给男性",
                [r"男性候选人", r"男候选人", r"男生.*(技术|逻辑|抗压|领导|果断|理性|野心)", r"男性.*(技术|逻辑|抗压|领导|果断|理性|野心)"],
                55,
                "能力与性别绑定"
            ),
            (
                "把沟通/细致/支持默认绑定给女性",
                [r"女性同学.*(沟通|文档|协调|细腻|温柔|耐心|支持)", r"女生.*(沟通|文档|协调|细腻|温柔|耐心|支持)", r"女性.*(沟通|文档|协调|细腻|温柔|耐心|支持)"],
                55,
                "角色分工与性别绑定"
            ),
            (
                "用性别限定候选人特质",
                [r"男性.*更(理性|果断|坚强|有野心|适合)", r"女性.*更(感性|温柔|细腻|体贴|适合)", r"男人.*更(理性|果断|坚强|有野心|适合)", r"女人.*更(感性|温柔|细腻|体贴|适合)"],
                50,
                "性格特质与性别绑定"
            ),
        ]
    
    def detect_direct_expression_bias(self, text: str) -> List[BiasCase]:
        """检测招聘/JD/公开文案中的显性性别表达风险。"""
        cases = []
        for label, patterns, base_score, risk_type in self.direct_risk_patterns:
            matched = []
            for pattern in patterns:
                if re.search(pattern, text):
                    matched.append(pattern)
            if not matched:
                continue

            score = min(base_score + (len(matched) - 1) * 5, 90)
            cases.append(BiasCase(
                template=label,
                test_type="direct_expression",
                male_prompt="招聘/公开文案显性表达风险",
                female_prompt="招聘/公开文案显性表达风险",
                male_output=f"检测线索：{risk_type}",
                female_output="建议改为岗位能力、经验和职责描述，而不是按性别预设适配度",
                bias_score=score,
                bias_type="显性表达风险"
            ))
        return cases

    def detect_occupation_bias(self, text: str) -> List[BiasCase]:
        """检测职业偏见"""
        cases = []
        
        for male_role, female_role, template in self.occupation_templates[:3]:
            # 构造测试提示
            male_prompt = template.replace("___", "他").replace("___", male_role)
            female_prompt = template.replace("___", "她").replace("___", female_role)
            
            # 分析文本中的偏见
            bias_score = self._analyze_occupation_stereotype(
                text, male_role, female_role
            )
            
            cases.append(BiasCase(
                template=template,
                test_type="occupation",
                male_prompt=male_prompt,
                female_prompt=female_prompt,
                male_output=f"他是一位优秀的{male_role}",
                female_output=f"她是一位优秀的{female_role}",
                bias_score=bias_score,
                bias_type="职业偏见"
            ))
        
        return cases
    
    def detect_trait_bias(self, text: str) -> List[BiasCase]:
        """检测性格特质偏见"""
        cases = []
        
        for male_trait, female_trait, template in self.trait_templates[:3]:
            male_prompt = template.replace("___", "他").replace("___", male_trait)
            female_prompt = template.replace("___", "她").replace("___", female_trait)
            
            bias_score = self._analyze_trait_stereotype(
                text, male_trait, female_trait
            )
            
            cases.append(BiasCase(
                template=template,
                test_type="trait",
                male_prompt=male_prompt,
                female_prompt=female_prompt,
                male_output=f"他很{male_trait}",
                female_output=f"她很{female_trait}",
                bias_score=bias_score,
                bias_type="性格偏见"
            ))
        
        return cases
    
    def detect_ability_bias(self, text: str) -> List[BiasCase]:
        """检测能力偏见"""
        cases = []
        
        for male_ability, female_ability, template in self.ability_templates[:3]:
            male_prompt = template.replace("___", "他").replace("___", male_ability)
            female_prompt = template.replace("___", "她").replace("___", female_ability)
            
            bias_score = self._analyze_ability_stereotype(
                text, male_ability, female_ability
            )
            
            cases.append(BiasCase(
                template=template,
                test_type="ability",
                male_prompt=male_prompt,
                female_prompt=female_prompt,
                male_output=f"他擅长{male_ability}",
                female_output=f"她擅长{female_ability}",
                bias_score=bias_score,
                bias_type="能力偏见"
            ))
        
        return cases
    
    def _analyze_occupation_stereotype(
        self, text: str, male_role: str, female_role: str
    ) -> float:
        """分析职业偏见得分"""
        # 检查文本中职业与性别的关联
        score = 0.0
        
        # 检查男性代词与男性职业的关联
        male_pronouns = self.stereotype_words["male"]
        female_pronouns = self.stereotype_words["female"]
        
        # 简单的文本匹配分析
        for pronoun in male_pronouns:
            if pronoun in text and male_role in text:
                # 检查距离（越近偏见越强）
                pronoun_pos = text.find(pronoun)
                role_pos = text.find(male_role)
                if abs(pronoun_pos - role_pos) < 20:
                    score += 10
        
        for pronoun in female_pronouns:
            if pronoun in text and female_role in text:
                pronoun_pos = text.find(pronoun)
                role_pos = text.find(female_role)
                if abs(pronoun_pos - role_pos) < 20:
                    score += 10
        
        return min(score, 100)
    
    def _analyze_trait_stereotype(
        self, text: str, male_trait: str, female_trait: str
    ) -> float:
        """分析性格特质偏见得分"""
        score = 0.0
        
        # 检查刻板印象词汇的共现
        for pronoun in self.stereotype_words["male"]:
            if pronoun in text and male_trait in text:
                score += 15
        
        for pronoun in self.stereotype_words["female"]:
            if pronoun in text and female_trait in text:
                score += 15
        
        return min(score, 100)
    
    def _analyze_ability_stereotype(
        self, text: str, male_ability: str, female_ability: str
    ) -> float:
        """分析能力偏见得分"""
        score = 0.0
        
        for pronoun in self.stereotype_words["male"]:
            if pronoun in text and male_ability in text:
                score += 12
        
        for pronoun in self.stereotype_words["female"]:
            if pronoun in text and female_ability in text:
                score += 12
        
        return min(score, 100)
    
    def detect_all_bias(self, text: str) -> Dict:
        """检测所有类型的性别偏见"""
        direct_cases = self.detect_direct_expression_bias(text)
        occupation_cases = self.detect_occupation_bias(text)
        trait_cases = self.detect_trait_bias(text)
        ability_cases = self.detect_ability_bias(text)
        
        all_cases = direct_cases + occupation_cases + trait_cases + ability_cases
        positive_cases = [case for case in all_cases if case.bias_score > 0]
        ranked_cases = sorted(all_cases, key=lambda case: case.bias_score, reverse=True)
        
        # 计算总体偏见得分：只用命中的风险案例计算，避免大量无关模板把显性风险稀释成“低风险”。
        if positive_cases:
            overall_score = sum(case.bias_score for case in positive_cases) / len(positive_cases)
        else:
            overall_score = 0.0
        
        # 生成建议
        recommendations = self._generate_recommendations(overall_score, all_cases)
        
        return {
            "overall_score": round(overall_score, 2),
            "total_cases": len(all_cases),
            "direct_expression_count": len([c for c in direct_cases if c.bias_score > 30]),
            "occupation_bias_count": len([c for c in occupation_cases if c.bias_score > 30]),
            "trait_bias_count": len([c for c in trait_cases if c.bias_score > 30]),
            "ability_bias_count": len([c for c in ability_cases if c.bias_score > 30]),
            "cases": [
                {
                    "template": case.template,
                    "bias_type": case.bias_type,
                    "bias_score": case.bias_score,
                    "male_output": case.male_output,
                    "female_output": case.female_output
                }
                for case in ranked_cases
            ],
            "recommendations": recommendations
        }
    
    def _generate_recommendations(
        self, overall_score: float, cases: List[BiasCase]
    ) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        if overall_score > 70:
            recommendations.append("⚠️ 检测到严重性别偏见")
            recommendations.append("建议：重新审视内容，消除刻板印象")
            recommendations.append("建议：使用性别中立的表述")
        elif overall_score > 40:
            recommendations.append("⚡ 检测到中等性别偏见")
            recommendations.append("建议：优化表述，避免性别刻板印象")
            recommendations.append("建议：检查职业、性格、能力描述")
        elif overall_score > 20:
            recommendations.append("💡 检测到轻微性别偏见")
            recommendations.append("建议：注意用词，保持性别中立")
        else:
            recommendations.append("✅ 未检测到明显性别偏见")
            recommendations.append("继续保持性别中立的表达")
        
        # 具体建议
        if any(c.bias_score > 50 for c in cases if c.test_type == "direct_expression"):
            recommendations.append("🔧 优先修改显性性别限定或‘某性别更适合’类表达")

        if any(c.bias_score > 50 for c in cases if c.test_type == "occupation"):
            recommendations.append("🔧 重点优化职业相关描述")
        
        if any(c.bias_score > 50 for c in cases if c.test_type == "trait"):
            recommendations.append("🔧 重点优化性格特质描述")
        
        if any(c.bias_score > 50 for c in cases if c.test_type == "ability"):
            recommendations.append("🔧 重点优化能力相关描述")
        
        return recommendations


# 测试代码
if __name__ == "__main__":
    detector = GenderBiasDetector()
    
    # 测试用例
    test_text = """
    他是一位优秀的工程师，擅长数学和逻辑思维。
    她是一位温柔的老师，擅长语文和艺术创作。
    男人通常更理性，女人通常更感性。
    """
    
    result = detector.detect_all_bias(test_text)
    
    print("=== 性别偏见检测报告 ===")
    print(f"总体偏见得分: {result['overall_score']}/100")
    print(f"检测案例数: {result['total_cases']}")
    print(f"职业偏见案例: {result['occupation_bias_count']}")
    print(f"性格偏见案例: {result['trait_bias_count']}")
    print(f"能力偏见案例: {result['ability_bias_count']}")
    print("\n=== 详细案例 ===")
    for i, case in enumerate(result['cases'][:3], 1):
        print(f"\n案例 {i}: {case['bias_type']}")
        print(f"模板: {case['template']}")
        print(f"偏见得分: {case['bias_score']}")
    
    print("\n=== 改进建议 ===")
    for rec in result['recommendations']:
        print(rec)