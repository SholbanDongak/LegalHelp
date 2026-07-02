"""
Калькулятор государственной пошлины по ст. 333.19 НК РФ
Актуальные ставки с 9 сентября 2024 года (ФЗ от 12.07.2024 № 258-ФЗ)
"""
from typing import Dict, Optional, Tuple
from enum import Enum


class ClaimType(Enum):
    """Тип иска"""
    PROPERTY = "property"  # Имущественный, подлежащий оценке
    NON_PROPERTY = "non_property"  # Неимущественный
    DIVORCE = "divorce"  # Расторжение брака
    ALIMONY = "alimony"  # Алименты
    LABOR = "labor"  # Трудовой спор
    CONSUMER = "consumer"  # Защита прав потребителей
    BANKRUPTCY = "bankruptcy"  # Банкротство
    OTHER = "other"  # Прочее


class PartyType(Enum):
    """Тип стороны"""
    INDIVIDUAL = "individual"  # Физическое лицо
    LEGAL = "legal"  # Юридическое лицо


def calculate_property_claim_duty(price: float, party_type: PartyType = PartyType.INDIVIDUAL) -> Tuple[float, str]:
    """
    Расчёт госпошлины для имущественных исков, подлежащих оценке.
    
    Args:
        price: Цена иска (руб.)
        party_type: Тип стороны (физлицо или юрлицо)
    
    Returns:
        (сумма госпошлины, формула расчёта)
    """
    if price <= 0:
        return 0, "Цена иска должна быть положительной"
    
    # С 09.09.2024 — новые ставки
    if price <= 100_000:
        duty = max(3_000, price * 0.03)
        formula = f"3% от {price:.2f} ₽ = {price * 0.03:.2f} ₽, но не менее 3 000 ₽"
    elif price <= 200_000:
        duty = 3_000 + (price - 100_000) * 0.02
        formula = f"3 000 ₽ + 2% от ({price:.2f} - 100 000) = {duty:.2f} ₽"
    elif price <= 1_000_000:
        duty = 5_000 + (price - 200_000) * 0.01
        formula = f"5 000 ₽ + 1% от ({price:.2f} - 200 000) = {duty:.2f} ₽"
    elif price <= 2_000_000:
        duty = 13_000 + (price - 1_000_000) * 0.005
        formula = f"13 000 ₽ + 0,5% от ({price:.2f} - 1 000 000) = {duty:.2f} ₽"
    else:
        duty = 18_000 + (price - 2_000_000) * 0.005
        duty = min(duty, 200_000)  # Максимум 200 000 ₽
        formula = f"18 000 ₽ + 0,5% от ({price:.2f} - 2 000 000) = {min(18_000 + (price - 2_000_000) * 0.005, 200_000):.2f} ₽ (макс. 200 000 ₽)"
    
    return duty, formula


def calculate_non_property_claim_duty(
    party_type: PartyType = PartyType.INDIVIDUAL,
    requirements_count: int = 1
) -> Tuple[float, str]:
    """
    Расчёт госпошлины для неимущественных исков.
    
    Args:
        party_type: Тип стороны
        requirements_count: Количество требований
    
    Returns:
        (сумма госпошлины, формула расчёта)
    """
    rate = 3_000 if party_type == PartyType.INDIVIDUAL else 6_000
    duty = rate * requirements_count
    
    if requirements_count == 1:
        formula = f"{rate:,} ₽ за 1 требование"
    else:
        formula = f"{rate:,} ₽ × {requirements_count} требований = {duty:,} ₽"
    
    return duty, formula


def calculate_divorce_duty() -> Tuple[float, str]:
    """Госпошлина за расторжение брака — 5 000 ₽ (с 09.09.2024)"""
    return 5_000, "Фиксированная ставка: 5 000 ₽ (ст. 333.19 НК РФ, пп. 5 п. 1)"


def calculate_alimony_duty() -> Tuple[float, str]:
    """Госпошлина за взыскание алиментов — 150 ₽"""
    return 150, "Льготная ставка: 150 ₽ (ст. 333.36 НК РФ)"


def calculate_labor_claim_duty() -> Tuple[float, str]:
    """Госпошлина по трудовым спорам — 0 ₽ (истец освобождён)"""
    return 0, "Истец освобождён от уплаты (ст. 333.36 НК РФ, пп. 1 п. 1)"


def calculate_consumer_claim_duty(price: Optional[float] = None) -> Tuple[float, str]:
    """
    Госпошлина по искам о защите прав потребителей.
    
    Args:
        price: Цена иска (если есть)
    
    Returns:
        (сумма госпошлины, формула расчёта)
    """
    if price is None or price <= 1_000_000:
        return 0, "Истец освобождён (цена иска до 1 млн ₽, ст. 17 ЗоЗПП)"
    else:
        # Если цена иска свыше 1 млн — по общим правилам
        duty, formula = calculate_property_claim_duty(price)
        return duty, f"По общим правилам (цена иска свыше 1 млн): {formula}"


def calculate_duty(
    claim_type: ClaimType,
    price: Optional[float] = None,
    party_type: PartyType = PartyType.INDIVIDUAL,
    requirements_count: int = 1
) -> Dict:
    """
    Универсальный калькулятор госпошлины.
    
    Args:
        claim_type: Тип иска
        price: Цена иска (для имущественных)
        party_type: Тип стороны
        requirements_count: Количество требований
    
    Returns:
        Словарь с результатом:
        {
            'duty': сумма,
            'formula': формула расчёта,
            'claim_type': тип иска,
            'legal_basis': правовое основание
        }
    """
    result = {
        'claim_type': claim_type.value,
        'party_type': party_type.value,
        'legal_basis': 'ст. 333.19 НК РФ (в ред. ФЗ от 12.07.2024 № 258-ФЗ)'
    }
    
    if claim_type == ClaimType.PROPERTY:
        if price is None:
            return {**result, 'duty': 0, 'formula': '❌ Укажите цену иска'}
        duty, formula = calculate_property_claim_duty(price, party_type)
        result.update({'duty': duty, 'formula': formula})
        
    elif claim_type == ClaimType.NON_PROPERTY:
        duty, formula = calculate_non_property_claim_duty(party_type, requirements_count)
        result.update({'duty': duty, 'formula': formula})
        
    elif claim_type == ClaimType.DIVORCE:
        duty, formula = calculate_divorce_duty()
        result.update({'duty': duty, 'formula': formula})
        
    elif claim_type == ClaimType.ALIMONY:
        duty, formula = calculate_alimony_duty()
        result.update({'duty': duty, 'formula': formula})
        
    elif claim_type == ClaimType.LABOR:
        duty, formula = calculate_labor_claim_duty()
        result.update({'duty': duty, 'formula': formula})
        
    elif claim_type == ClaimType.CONSUMER:
        duty, formula = calculate_consumer_claim_duty(price)
        result.update({'duty': duty, 'formula': formula})
        
    else:
        result.update({'duty': 0, 'formula': '⚠️ Тип иска не определён'})
    
    return result


# ===== ТЕСТЫ =====
if __name__ == "__main__":
    print("=" * 70)
    print("ТЕСТЫ КАЛЬКУЛЯТОРА ГОСПОШЛИНЫ (актуально с 09.09.2024)")
    print("=" * 70)
    
    tests = [
        ("Имущественный иск, 50 000 ₽", ClaimType.PROPERTY, 50_000, PartyType.INDIVIDUAL, 1),
        ("Имущественный иск, 100 000 ₽", ClaimType.PROPERTY, 100_000, PartyType.INDIVIDUAL, 1),
        ("Имущественный иск, 150 000 ₽", ClaimType.PROPERTY, 150_000, PartyType.INDIVIDUAL, 1),
        ("Имущественный иск, 500 000 ₽", ClaimType.PROPERTY, 500_000, PartyType.INDIVIDUAL, 1),
        ("Имущественный иск, 1 500 000 ₽", ClaimType.PROPERTY, 1_500_000, PartyType.INDIVIDUAL, 1),
        ("Имущественный иск, 3 000 000 ₽", ClaimType.PROPERTY, 3_000_000, PartyType.INDIVIDUAL, 1),
        ("Неимущественный иск, 1 требование", ClaimType.NON_PROPERTY, None, PartyType.INDIVIDUAL, 1),
        ("Неимущественный иск, 3 требования", ClaimType.NON_PROPERTY, None, PartyType.INDIVIDUAL, 3),
        ("Расторжение брака", ClaimType.DIVORCE, None, PartyType.INDIVIDUAL, 1),
        ("Взыскание алиментов", ClaimType.ALIMONY, None, PartyType.INDIVIDUAL, 1),
        ("Трудовой спор", ClaimType.LABOR, None, PartyType.INDIVIDUAL, 1),
        ("ЗоЗПП, цена иска 50 000 ₽", ClaimType.CONSUMER, 50_000, PartyType.INDIVIDUAL, 1),
        ("ЗоЗПП, цена иска 2 000 000 ₽", ClaimType.CONSUMER, 2_000_000, PartyType.INDIVIDUAL, 1),
    ]
    
    for name, claim_type, price, party_type, req_count in tests:
        result = calculate_duty(claim_type, price, party_type, req_count)
        print(f"\n{name}:")
        print(f"  💰 Госпошлина: {result['duty']:,.2f} ₽")
        print(f"  📝 Формула: {result['formula']}")
