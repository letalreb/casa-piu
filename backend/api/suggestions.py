"""
AI Suggestions endpoint
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_database
from models import User, Asset, Expense
from schemas import AISuggestionRequest, AISuggestionResponse, ResponseWrapper
from utils.auth import get_current_user
from datetime import datetime, timedelta
from decimal import Decimal
import logging
import os

logger = logging.getLogger(__name__)
router = APIRouter()

# Check which AI service is available
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

@router.post("/ai", response_model=ResponseWrapper)
async def get_ai_suggestions(
    request: AISuggestionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Get AI-powered saving suggestions based on expenses"""
    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=request.period_months * 30)
        
        # Get expenses in the period
        query = db.query(Expense).filter(
            Expense.user_id == current_user.id,
            Expense.created_at >= start_date
        )
        
        if request.asset_id:
            query = query.filter(Expense.asset_id == request.asset_id)
        
        expenses = query.all()
        
        # Prepare expense summary
        total_amount = sum(float(e.amount) for e in expenses)
        category_totals = {}
        for expense in expenses:
            category = expense.category
            category_totals[category] = category_totals.get(category, 0) + float(expense.amount)
        
        # Generate suggestions based on expense data
        suggestions = []
        potential_savings = Decimal("0")
        
        # Simple rule-based suggestions (fallback if no AI available)
        if total_amount > 0:
            # High expense categories
            for category, amount in sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:3]:
                if amount > total_amount * 0.2:  # More than 20% of total
                    suggestions.append(
                        f"La categoria '{category}' rappresenta una spesa significativa "
                        f"(€{amount:.2f}). Considera di confrontare fornitori alternativi."
                    )
                    potential_savings += Decimal(str(amount * 0.1))  # Estimate 10% savings
        
        # IMU optimization suggestions
        properties = db.query(Asset).filter(
            Asset.user_id == current_user.id,
            Asset.type == "property"
        ).all()
        
        for prop in properties:
            if prop.details_json and 'rendita' in prop.details_json:
                suggestions.append(
                    f"Per {prop.name}: verifica se hai diritto a detrazioni IMU "
                    f"(prima casa, terreni agricoli, ecc.)"
                )
        
        # Vehicle suggestions
        vehicles = db.query(Asset).filter(
            Asset.user_id == current_user.id,
            Asset.type == "vehicle"
        ).all()
        
        if len(vehicles) > 2:
            suggestions.append(
                f"Hai {len(vehicles)} veicoli registrati. Valuta se tutti sono necessari "
                f"per ridurre i costi di assicurazione e manutenzione."
            )
        
        # Generic suggestions
        if not suggestions:
            suggestions = [
                "Continua a monitorare le tue spese per identificare opportunità di risparmio.",
                "Imposta promemoria per le scadenze per evitare more e interessi.",
                "Utilizza le automazioni per calcolare IMU e generare F24 in anticipo."
            ]
        
        # Try to use AI if available
        analysis = await generate_ai_analysis(expenses, suggestions)
        
        return ResponseWrapper(
            success=True,
            message="AI suggestions generated successfully",
            data=AISuggestionResponse(
                suggestions=suggestions,
                potential_savings=potential_savings,
                analysis=analysis
            )
        )
        
    except Exception as e:
        logger.error(f"AI suggestions error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate AI suggestions"
        )

async def generate_ai_analysis(expenses, suggestions):
    """Generate AI analysis using OpenAI or Anthropic"""
    try:
        if ANTHROPIC_API_KEY:
            return await generate_anthropic_analysis(expenses, suggestions)
        elif OPENAI_API_KEY:
            return await generate_openai_analysis(expenses, suggestions)
        else:
            return "Analisi AI non disponibile. Installa OpenAI o Anthropic API."
    except Exception as e:
        logger.error(f"AI analysis error: {str(e)}")
        return "Analisi automatica basata sui dati delle spese."

async def generate_anthropic_analysis(expenses, suggestions):
    """Generate analysis using Anthropic Claude"""
    try:
        import anthropic
        
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        
        expense_summary = "\n".join([
            f"- {e.category}: €{e.amount} ({e.status})"
            for e in expenses[:10]  # Limit to 10 recent expenses
        ])
        
        message = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": f"""Analizza queste spese familiari e fornisci consigli per risparmiare:

{expense_summary}

Suggerimenti già generati:
{chr(10).join(f"- {s}" for s in suggestions)}

Fornisci un'analisi breve (2-3 frasi) con consigli pratici in italiano."""
            }]
        )
        
        return message.content[0].text
        
    except Exception as e:
        logger.error(f"Anthropic analysis error: {str(e)}")
        return "Analisi automatica basata sui dati delle spese."

async def generate_openai_analysis(expenses, suggestions):
    """Generate analysis using OpenAI"""
    try:
        import openai
        
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        expense_summary = "\n".join([
            f"- {e.category}: €{e.amount} ({e.status})"
            for e in expenses[:10]
        ])
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user",
                "content": f"""Analizza queste spese familiari e fornisci consigli per risparmiare:

{expense_summary}

Suggerimenti già generati:
{chr(10).join(f"- {s}" for s in suggestions)}

Fornisci un'analisi breve (2-3 frasi) con consigli pratici in italiano."""
            }],
            max_tokens=300
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"OpenAI analysis error: {str(e)}")
        return "Analisi automatica basata sui dati delle spese."