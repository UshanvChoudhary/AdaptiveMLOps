import os
import re

def to_async_db(content):
    content = content.replace("from sqlalchemy.orm import Session", "from sqlalchemy.ext.asyncio import AsyncSession\nfrom sqlalchemy.future import select")
    content = content.replace("db: Session", "db: AsyncSession")
    
    # db.commit() -> await db.commit()
    content = content.replace("db.commit()", "await db.commit()")
    content = content.replace("db.refresh(", "await db.refresh(")
    content = content.replace("db.rollback()", "await db.rollback()")
    
    # db.query(X).filter(Y).first() -> (await db.execute(select(X).filter(Y))).scalars().first()
    # db.query(X).filter(Y).all() -> (await db.execute(select(X).filter(Y))).scalars().all()
    # db.query(X).offset(skip).limit(limit).all() -> (await db.execute(select(X).offset(skip).limit(limit))).scalars().all()
    
    def repl_query(m):
        inner = m.group(1) # The whole query chain
        # Extract the model being queried
        q_match = re.search(r'db\.query\((.*?)\)', inner)
        if not q_match: return m.group(0)
        model = q_match.group(1)
        
        rest = inner[q_match.end():]
        # e.g. rest = ".filter(X).first()"
        
        # Check if it ends with .first() or .all()
        if rest.endswith('.first()'):
            rest = rest[:-8]
            return f"(await db.execute(select({model}){rest})).scalars().first()"
        elif rest.endswith('.all()'):
            rest = rest[:-6]
            # Need to handle .unique().all() if there are joinedloads
            if 'joinedload' in rest:
                return f"(await db.execute(select({model}){rest})).unique().scalars().all()"
            return f"(await db.execute(select({model}){rest})).scalars().all()"
        
        return m.group(0)

    # We need to find the full db.query chain. 
    # This is tricky with regex. Let's do it manually on a line-by-line or statement level.
    
    # Actually, a simpler regex for db.query(X).Y.Z.all() 
    # db\.query\((.*?)\)(.*?)\.all\(\) -> (await db.execute(select(\1)\2)).scalars().all()
    # db\.query\((.*?)\)(.*?)\.first\(\) -> (await db.execute(select(\1)\2)).scalars().first()
    
    content = re.sub(r'db\.query\((.*?)\)((?:\.[a-zA-Z_]+\(.*?\))*)\.all\(\)', lambda m: f"(await db.execute(select({m.group(1)}){m.group(2)})).unique().scalars().all()" if "joinedload" in m.group(2) else f"(await db.execute(select({m.group(1)}){m.group(2)})).scalars().all()", content)
    
    content = re.sub(r'db\.query\((.*?)\)((?:\.[a-zA-Z_]+\(.*?\))*)\.first\(\)', lambda m: f"(await db.execute(select({m.group(1)}){m.group(2)})).scalars().first()", content)

    # Any remaining db.query(X).order_by(Y).first()
    content = re.sub(r'db\.query\((.*?)\)\.order_by\((.*?)\)\.first\(\)', r'(await db.execute(select(\1).order_by(\2))).scalars().first()', content)
    
    # Def -> async def
    content = re.sub(r'^def ', 'async def ', content, flags=re.MULTILINE)
    
    return content

for root, _, files in os.walk('backend/app/services'):
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
            content = to_async_db(content)
            with open(path, 'w', encoding='utf-8') as file:
                file.write(content)

print("Services refactored.")
