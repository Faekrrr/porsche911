from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.user import User, UserResponse, UserUpdate, Portfolio, PortfolioCreate, Highlight, HighlightCreate, Star
from database import SessionLocal
from typing import List
from datetime import datetime

user_router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@user_router.get("/users/me", response_model=UserResponse)
async def get_current_user(db: Session = Depends(get_db)):
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@user_router.put("/users/me", response_model=UserResponse)
async def update_current_user(user_update: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user

@user_router.post("/users/me/portfolio", response_model=PortfolioCreate)
async def add_portfolio_item(
    portfolio_data: PortfolioCreate, 
    db: Session = Depends(get_db), 
    current_user=Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    new_portfolio = Portfolio(
        name=portfolio_data.name,
        repo_link=portfolio_data.repo_link,
        description=portfolio_data.description,
        tags=portfolio_data.tags,
        user_id=current_user.id
    )

    db.add(new_portfolio)
    db.commit()
    db.refresh(new_portfolio)

    if portfolio_data.collaborators:
        collaborators = db.query(User).filter(User.id.in_(portfolio_data.collaborators)).all()
        new_portfolio.collaborators.extend(collaborators)
        db.commit()

    return new_portfolio

@user_router.post("/users/portfolio/{portfolio_id}/highlights", response_model=HighlightCreate)
async def add_highlight(
    portfolio_id: int, 
    highlight_data: HighlightCreate, 
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    new_highlight = Highlight(
        media_url=highlight_data.media_url,
        description=highlight_data.description,
        tags=highlight_data.tags,
        created_at=datetime.utcnow(),
        portfolio_id=portfolio_id
    )

    db.add(new_highlight)
    db.commit()
    db.refresh(new_highlight)
    return new_highlight

@user_router.delete("/users/portfolio/{portfolio_id}/highlights/{highlight_id}", status_code=204)
async def remove_highlight(
    portfolio_id: int,
    highlight_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    highlight = db.query(Highlight).filter(Highlight.id == highlight_id, Highlight.portfolio_id == portfolio_id).first()
    if not highlight:
        raise HTTPException(status_code=404, detail="Highlight not found")

    db.delete(highlight)
    db.commit()

    return

@user_router.get("/users/me/portfolio", response_model=List[PortfolioCreate])
async def get_my_portfolios(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    skip: int = 0,
    limit: int = 10
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    portfolios = db.query(Portfolio).filter(Portfolio.user_id == current_user.id).offset(skip).limit(limit).all()
    return portfolios

@user_router.get("/users/portfolio/{portfolio_id}", response_model=PortfolioCreate)
async def get_portfolio_item(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return portfolio

@user_router.get("/users/{username}/portfolio", response_model=List[PortfolioCreate])
async def get_user_portfolios_by_username(
    username: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    skip: int = 0,
    limit: int = 10
):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    portfolios = db.query(Portfolio).filter(Portfolio.user_id == user.id).offset(skip).limit(limit).all()

    visible_portfolios = []
    for portfolio in portfolios:
        collaborators_ids = [collaborator.id for collaborator in portfolio.collaborators]
        if not portfolio.is_private or (current_user and (current_user.id in portfolio.allowed_users or current_user.id in collaborators_ids)):
            visible_portfolios.append(portfolio)

    return visible_portfolios

@user_router.delete("/users/portfolio/{portfolio_id}", status_code=204)
async def delete_portfolio(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id).first()

    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found or you don't have permission to delete it")

    db.delete(portfolio)
    db.commit()

    return {"message": "Portfolio deleted successfully"}

@user_router.put("/users/me/portfolio/{portfolio_id}", response_model=PortfolioCreate)
async def update_portfolio(
    portfolio_id: int,
    portfolio_data: PortfolioCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id).first()

    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found or you don't have permission to modify it")

    portfolio.name = portfolio_data.name
    portfolio.repo_link = portfolio_data.repo_link
    portfolio.description = portfolio_data.description
    portfolio.tags = portfolio_data.tags
    portfolio.is_private = portfolio_data.is_private
    portfolio.allowed_users = portfolio_data.allowed_users

    if portfolio_data.collaborators:
        collaborators = db.query(User).filter(User.id.in_(portfolio_data.collaborators)).all()
        portfolio.collaborators = collaborators

    db.commit()
    db.refresh(portfolio)
    return portfolio

@user_router.post("/users/portfolio/{portfolio_id}/star", status_code=201)
async def give_star_to_portfolio(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    existing_star = db.query(Star).filter(
        Star.user_id == current_user.id, Star.portfolio_id == portfolio_id
    ).first()
    if existing_star:
        raise HTTPException(status_code=400, detail="You have already starred this portfolio")

    new_star = Star(user_id=current_user.id, portfolio_id=portfolio_id, created_at=datetime.utcnow())
    db.add(new_star)

    portfolio.star_count += 1
    db.commit()
    return {"message": "Star added successfully"}

@user_router.delete("/users/portfolio/{portfolio_id}/star", status_code=204)
async def remove_star_from_portfolio(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    star = db.query(Star).filter(
        Star.user_id == current_user.id, Star.portfolio_id == portfolio_id
    ).first()
    if not star:
        raise HTTPException(status_code=404, detail="Star not found")

    db.delete(star)

    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if portfolio:
        portfolio.star_count -= 1
    db.commit()
    return