"""
IMU (Imposta Municipale Unica) calculation utilities
"""
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# IMU rates and coefficients for 2024
IMU_COEFFICIENTS = {
    "A/1": Decimal("1.05"),  # Abitazioni di tipo signorile
    "A/2": Decimal("1.05"),  # Abitazioni di tipo civile
    "A/3": Decimal("1.05"),  # Abitazioni di tipo economico
    "A/4": Decimal("1.05"),  # Abitazioni di tipo popolare
    "A/5": Decimal("1.05"),  # Abitazioni di tipo ultrapopolare
    "A/6": Decimal("1.05"),  # Abitazioni di tipo rurale
    "A/7": Decimal("1.05"),  # Abitazioni in villini
    "A/8": Decimal("1.05"),  # Abitazioni in ville
    "A/9": Decimal("1.05"),  # Castelli, palazzi di eminenti pregi artistici
    "A/10": Decimal("1.05"), # Uffici e studi privati
    "A/11": Decimal("1.05"), # Abitazioni ed alloggi tipici dei luoghi
    "B/1": Decimal("1.05"),  # Collegi e convitti, educandati, ricoveri, orfanotrofi
    "B/2": Decimal("1.05"),  # Case di cura ed ospedali
    "B/3": Decimal("1.05"),  # Prigioni e riformatori
    "B/4": Decimal("1.05"),  # Uffici pubblici
    "B/5": Decimal("1.05"),  # Scuole, laboratori scientifici
    "B/6": Decimal("1.05"),  # Biblioteche, pinacoteche, musei, gallerie
    "B/7": Decimal("1.05"),  # Cappelle ed oratori non destinati all'esercizio pubblico
    "B/8": Decimal("1.05"),  # Magazzini sotterranei per depositi di derrate
    "C/1": Decimal("1.05"),  # Negozi e botteghe
    "C/2": Decimal("1.05"),  # Magazzini e locali di deposito
    "C/3": Decimal("1.05"),  # Laboratori per arti e mestieri
    "C/4": Decimal("1.05"),  # Fabbricati e locali per esercizi sportivi
    "C/5": Decimal("1.05"),  # Stabilimenti balneari e di acque curative
    "C/6": Decimal("1.05"),  # Stalle, scuderie, rimesse, autorimesse
    "C/7": Decimal("1.05"),  # Tettoie chiuse od aperte
    "D/1": Decimal("1.05"),  # Opifici
    "D/2": Decimal("1.05"),  # Alberghi e pensioni
    "D/3": Decimal("1.05"),  # Teatri, cinematografi, sale per concerti
    "D/4": Decimal("1.05"),  # Case di cura private
    "D/5": Decimal("1.05"),  # Istituti di credito, cambio e assicurazione
    "D/6": Decimal("1.05"),  # Fabbricati e locali per esercizi sportivi
    "D/7": Decimal("1.05"),  # Fabbricati costruiti per le speciali esigenze
    "D/8": Decimal("1.05"),  # Fabbricati costruiti per le speciali esigenze
    "D/9": Decimal("1.05"),  # Edifici galleggianti o sospesi
    "D/10": Decimal("1.05"), # Fabbricati per funzioni produttive
}

# Default IMU rates (may vary by municipality)
DEFAULT_IMU_RATES = {
    "prima_casa": Decimal("0.4"),     # 0.4% for primary residence
    "altri_immobili": Decimal("0.86"), # 0.86% for other properties
    "fabbricati_rurali": Decimal("0.1"), # 0.1% for rural buildings
}

class IMUCalculator:
    """Calculator for IMU (Imposta Municipale Unica)"""
    
    def __init__(self):
        pass
    
    def calculate_base_imponibile(self, rendita: Decimal, categoria: str) -> Decimal:
        """Calculate IMU taxable base (base imponibile)"""
        try:
            coefficient = IMU_COEFFICIENTS.get(categoria, Decimal("1.05"))
            base_imponibile = rendita * coefficient * Decimal("160")
            return base_imponibile.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        except Exception as e:
            logger.error(f"Error calculating base imponibile: {str(e)}")
            raise
    
    def calculate_imu_annual(
        self,
        rendita: Decimal,
        categoria: str,
        aliquota: Decimal = None,
        is_prima_casa: bool = False,
        detrazione_prima_casa: Decimal = Decimal("200")
    ) -> Dict[str, Any]:
        """Calculate annual IMU amount"""
        try:
            # Calculate taxable base
            base_imponibile = self.calculate_base_imponibile(rendita, categoria)
            
            # Determine tax rate
            if aliquota is None:
                aliquota = DEFAULT_IMU_RATES["prima_casa"] if is_prima_casa else DEFAULT_IMU_RATES["altri_immobili"]
            
            # Calculate gross IMU
            imu_lordo = base_imponibile * (aliquota / Decimal("100"))
            
            # Apply primary residence deduction
            detrazione = detrazione_prima_casa if is_prima_casa else Decimal("0")
            imu_netto = max(imu_lordo - detrazione, Decimal("0"))
            
            # Split into two installments
            primo_acconto = (imu_netto / Decimal("2")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            secondo_acconto = imu_netto - primo_acconto
            
            return {
                "base_imponibile": base_imponibile,
                "aliquota": aliquota,
                "imu_lordo": imu_lordo,
                "detrazione": detrazione,
                "imu_netto": imu_netto,
                "primo_acconto": primo_acconto,
                "secondo_acconto": secondo_acconto,
                "scadenza_primo": "16/06",
                "scadenza_secondo": "16/12"
            }
            
        except Exception as e:
            logger.error(f"Error calculating annual IMU: {str(e)}")
            raise
    
    def calculate_imu_for_property(self, property_details: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate IMU for a specific property"""
        try:
            rendita = Decimal(str(property_details.get("rendita", "0")))
            categoria = property_details.get("categoria_catastale", "A/2")
            is_prima_casa = property_details.get("prima_casa", False)
            aliquota_custom = property_details.get("aliquota")
            
            aliquota = Decimal(str(aliquota_custom)) if aliquota_custom else None
            
            if rendita <= 0:
                raise ValueError("Rendita catastale must be greater than 0")
            
            result = self.calculate_imu_annual(
                rendita=rendita,
                categoria=categoria,
                aliquota=aliquota,
                is_prima_casa=is_prima_casa
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating IMU for property: {str(e)}")
            raise

def get_imu_info_by_comune(comune: str) -> Dict[str, Any]:
    """Get IMU information by municipality (placeholder implementation)"""
    # In a real implementation, this would fetch data from an API or database
    # containing municipality-specific IMU rates and deductions
    return {
        "aliquota_prima_casa": Decimal("0.4"),
        "aliquota_altri_immobili": Decimal("0.86"),
        "detrazione_prima_casa": Decimal("200"),
        "maggiorazione_disponibile": True,
        "scadenze": ["16/06", "16/12"]
    }

def validate_categoria_catastale(categoria: str) -> bool:
    """Validate cadastral category"""
    return categoria in IMU_COEFFICIENTS

def get_available_categories() -> Dict[str, str]:
    """Get list of available cadastral categories with descriptions"""
    categories = {
        "A/1": "Abitazioni di tipo signorile",
        "A/2": "Abitazioni di tipo civile", 
        "A/3": "Abitazioni di tipo economico",
        "A/4": "Abitazioni di tipo popolare",
        "A/5": "Abitazioni di tipo ultrapopolare",
        "A/6": "Abitazioni di tipo rurale",
        "A/7": "Abitazioni in villini",
        "A/8": "Abitazioni in ville",
        "A/9": "Castelli, palazzi di eminenti pregi artistici",
        "A/10": "Uffici e studi privati",
        "A/11": "Abitazioni ed alloggi tipici dei luoghi",
        "C/1": "Negozi e botteghe",
        "C/2": "Magazzini e locali di deposito",
        "C/3": "Laboratori per arti e mestieri",
        "C/6": "Stalle, scuderie, rimesse, autorimesse",
        "C/7": "Tettoie chiuse od aperte"
    }
    return categories