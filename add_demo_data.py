import asyncio
import asyncpg
from datetime import datetime, timedelta
import uuid

async def add_demo_data():
    try:
        # Connect to database
        conn = await asyncpg.connect(
            host='localhost',
            port=5435,
            user='harvestnet',
            password='password123',
            database='harvestnet'
        )
        print("✅ Connected to database")
        
        # Create a demo farm if not exists
        farm_id = uuid.uuid4()
        await conn.execute("""
            INSERT INTO farms (id, name, location, created_at)
            VALUES ($1, $2, $3, NOW())
            ON CONFLICT (id) DO NOTHING
        """, farm_id, "Demo Farm", "Sample Location")
        print("✅ Farm created")
        
        # Check if batches already exist
        existing_batches = await conn.fetchval("SELECT COUNT(*) FROM batches")
        if existing_batches > 0:
            print(f"⚠️  Database already has {existing_batches} batches. Skipping demo data.")
            await conn.close()
            return
        
        # Add demo batches
        batches = [
            {
                "crop_type": "maize",
                "variety": "DK 777",
                "quantity": 2500,
                "location": "Bin A - North Section",
                "harvest_date": datetime.now() - timedelta(days=5),
                "sell_by": datetime.now() + timedelta(days=45),
                "safe_days": 45,
                "mold_risk": 8
            },
            {
                "crop_type": "rice",
                "variety": "Basmati",
                "quantity": 1800,
                "location": "Silo 2",
                "harvest_date": datetime.now() - timedelta(days=10),
                "sell_by": datetime.now() + timedelta(days=60),
                "safe_days": 60,
                "mold_risk": 4
            },
            {
                "crop_type": "wheat",
                "variety": "Sharbati",
                "quantity": 3200,
                "location": "Bin B - South Section",
                "harvest_date": datetime.now() - timedelta(days=2),
                "sell_by": datetime.now() + timedelta(days=30),
                "safe_days": 30,
                "mold_risk": 12
            },
            {
                "crop_type": "tomato",
                "variety": "Cherry",
                "quantity": 500,
                "location": "Cold Room A",
                "harvest_date": datetime.now() - timedelta(days=1),
                "sell_by": datetime.now() + timedelta(days=7),
                "safe_days": 7,
                "mold_risk": 25
            },
            {
                "crop_type": "potato",
                "variety": "Russet",
                "quantity": 4500,
                "location": "Root Cellar",
                "harvest_date": datetime.now() - timedelta(days=15),
                "sell_by": datetime.now() + timedelta(days=90),
                "safe_days": 90,
                "mold_risk": 3
            }
        ]
        
        for batch in batches:
            batch_id = uuid.uuid4()
            await conn.execute("""
                INSERT INTO batches (
                    id, farm_id, crop_type, variety, 
                    initial_quantity_kg, current_quantity_kg,
                    storage_location, harvest_date, expected_sell_by,
                    safe_days_remaining, mold_risk_percent, status, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, NOW())
            """,
                batch_id, farm_id, batch["crop_type"], batch["variety"],
                batch["quantity"], batch["quantity"],
                batch["location"], batch["harvest_date"], batch["sell_by"],
                batch["safe_days"], batch["mold_risk"], "active"
            )
            print(f"✅ Added {batch['quantity']}kg of {batch['crop_type']}")
        
        # Add some sensor readings for each batch
        batches_list = await conn.fetch("SELECT id FROM batches")
        for batch_record in batches_list:
            for i in range(0, 24, 2):  # Every 2 hours for 24 hours
                temp = 22 + (i % 8)  # Temperature varies 22-30
                humidity = 55 + (i % 20)  # Humidity varies 55-75
                co2 = 400 + (i % 100)  # CO2 varies 400-500
                
                await conn.execute("""
                    INSERT INTO sensor_readings (
                        id, batch_id, temperature, humidity, co2, timestamp
                    ) VALUES (
                        $1, $2, $3, $4, $5, NOW() - ($6 || ' hours')::interval
                    )
                """,
                    uuid.uuid4(), batch_record['id'], temp, humidity, co2, i
                )
            print(f"✅ Added sensor readings for batch {batch_record['id'][:8]}...")
        
        print("\n🎉 Demo data added successfully!")
        
        # Show summary
        count = await conn.fetchval("SELECT COUNT(*) FROM batches")
        sensor_count = await conn.fetchval("SELECT COUNT(*) FROM sensor_readings")
        print(f"\n📊 Database Summary:")
        print(f"   - Farms: 1")
        print(f"   - Batches: {count}")
        print(f"   - Sensor Readings: {sensor_count}")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure:")
        print("1. Docker containers are running: docker-compose ps")
        print("2. PostgreSQL is healthy: docker-compose logs postgres")
        print("3. You're in the correct directory")

if __name__ == "__main__":
    asyncio.run(add_demo_data())
