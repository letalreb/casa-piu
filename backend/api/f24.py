"""
F24 and IMU calculation endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_database
from models import User, Asset
from schemas import IMUCalculationRequest, IMUCalculationResponse, ResponseWrapper
from utils.auth import get_current_user
from utils.imu_calc import IMUCalculator
from utils.f24_pdf import F24Generator
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/calculate-imu", response_model=ResponseWrapper)
async def calculate_imu(
    request: IMUCalculationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Calculate IMU for property"""
    try:
        calculator = IMUCalculator()
        
        # Calculate IMU
        result = calculator.calculate_imu_annual(
            rendita=request.rendita,
            categoria=request.categoria,
            is_prima_casa=False  # Can be customized
        )
        
        response_data = IMUCalculationResponse(
            importo_primo_acconto=result["primo_acconto"],
            importo_secondo_acconto=result["secondo_acconto"],
            totale_annuo=result["imu_netto"],
            scadenza_primo=result["scadenza_primo"],
            scadenza_secondo=result["scadenza_secondo"]
        )
        
        return ResponseWrapper(
            success=True,
            message="IMU calculated successfully",
            data=response_data
        )
        
    except Exception as e:
        logger.error(f"IMU calculation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="IMU calculation failed"
        )

@router.post("/generate", response_model=ResponseWrapper)
async def generate_f24(
    asset_id: int,
    payment_type: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Generate F24 PDF for IMU payment"""
    try:
        # Get asset
        asset = db.query(Asset).filter(
            Asset.id == asset_id,
            Asset.user_id == current_user.id
        ).first()
        
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found"
            )
        
        if asset.type != "property":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="F24 can only be generated for properties"
            )
        
        # Calculate IMU
        calculator = IMUCalculator()
        imu_result = calculator.calculate_imu_for_property(asset.details_json)
        
        # Generate F24 PDF
        generator = F24Generator()
        
        # Prepare taxpayer data
        taxpayer_data = {
            "codice_fiscale": current_user.supabase_id[:16],  # Placeholder
            "nome_completo": current_user.name,
            "indirizzo": "Via Example 123",
            "comune": asset.details_json.get("comune", ""),
            "cap": "00100",
            "provincia": "RM"
        }
        
        f24_path = generator.generate_imu_f24(
            taxpayer_data=taxpayer_data,
            property_data=asset.details_json,
            imu_calculation=imu_result,
            payment_type=payment_type
        )
        
        # Return file URL
        file_url = f"/static/f24/{f24_path.split('/')[-1]}"
        
        return ResponseWrapper(
            success=True,
            message="F24 generated successfully",
            data={"file_url": file_url, "path": f24_path}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"F24 generation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="F24 generation failed"
        )