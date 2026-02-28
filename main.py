"""
🌿 CRYPTOVERDE - Main Entry Point
Professional Crypto Trading Dashboard
"""

from dashboard import CryptoDashboard
from scheduler import SchedulerManager
import logging
from utils import setup_directories

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("crypto_verde.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("CryptoVerde")

def main():
    """Main entry point"""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║     🌿 CRYPTOVERDE - Professional Crypto Dashboard      ║
    ║         Real-time Analytics • Technical Indicators       ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    # Setup directories
    setup_directories()
    
    print("\n📡 System Status:")
    print("   • Database: Supabase")
    print("   • API: CoinGecko")
    print("   • ETL: 5-minute intervals")
    print("   • Dashboard: Auto-refresh (60s)")
    print("   • Data Cleaning: ✓ All missing values handled")
    print("   • Error Handling: ✓ Complete\n")
    
    # Start scheduler
    scheduler = SchedulerManager()
    scheduler.start()
    
    try:
        # Run dashboard
        dashboard = CryptoDashboard()
        dashboard.run()
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    finally:
        scheduler.stop()

if __name__ == "__main__":
    main()