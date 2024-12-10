import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class XExchangeAPRCalculator:
    def __init__(self):
        self.base_url = "https://api.xexchange.com"  # Replace with actual API base URL
        self.api_endpoints = {
            "pairs": "/pairs",
            "farm": "/farm",
            "stats": "/stats"
        }
        
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make API request to xExchange"""
        try:
            response = requests.get(f"{self.base_url}{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making request: {e}")
            return {}

    def get_pool_info(self, pair_address: str) -> Dict:
        """Get pool information including reserves and token details"""
        params = {"pair": pair_address}
        return self._make_request(self.api_endpoints["pairs"], params)

    def get_farm_info(self, farm_address: str) -> Dict:
        """Get farming pool information including rewards and TVL"""
        params = {"farm": farm_address}
        return self._make_request(self.api_endpoints["farm"], params)

    def get_pool_stats(self, pair_address: str, days: int = 7) -> Dict:
        """Get pool statistics including volume and fees"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        params = {
            "pair": pair_address,
            "from": start_date.strftime("%Y-%m-%d"),
            "to": end_date.strftime("%Y-%m-%d")
        }
        return self._make_request(self.api_endpoints["stats"], params)

    def calculate_swap_apr(self, pair_address: str) -> float:
        """Calculate swap APR based on trading volume and fees"""
        stats = self.get_pool_stats(pair_address)
        pool_info = self.get_pool_info(pair_address)
        
        if not stats or not pool_info:
            return 0.0

        # Extract relevant data
        daily_volume = stats.get("volume_24h", 0)
        fee_percentage = pool_info.get("fee_percentage", 0.003)  # Default 0.3%
        tvl = pool_info.get("tvl_usd", 0)

        if tvl == 0:
            return 0.0

        # Calculate daily fees
        daily_fees = daily_volume * fee_percentage
        
        # Annualize (multiply by 365 days)
        annual_fees = daily_fees * 365
        
        # Calculate APR
        swap_apr = (annual_fees / tvl) * 100
        
        return swap_apr

    def calculate_farm_apr(self, farm_address: str) -> float:
        """Calculate farming APR based on reward emissions"""
        farm_info = self.get_farm_info(farm_address)
        
        if not farm_info:
            return 0.0

        # Extract relevant data
        reward_token_price = farm_info.get("reward_token_price", 0)
        rewards_per_day = farm_info.get("rewards_per_day", 0)
        tvl = farm_info.get("tvl_usd", 0)

        if tvl == 0:
            return 0.0

        # Calculate daily rewards in USD
        daily_rewards_usd = rewards_per_day * reward_token_price
        
        # Annualize rewards
        annual_rewards_usd = daily_rewards_usd * 365
        
        # Calculate APR
        farm_apr = (annual_rewards_usd / tvl) * 100
        
        return farm_apr

    def get_total_apr(self, pair_address: str, farm_address: Optional[str] = None) -> Dict[str, float]:
        """Calculate total APR including both swap and farming rewards"""
        swap_apr = self.calculate_swap_apr(pair_address)
        farm_apr = self.calculate_farm_apr(farm_address) if farm_address else 0.0
        
        return {
            "swap_apr": swap_apr,
            "farm_apr": farm_apr,
            "total_apr": swap_apr + farm_apr
        }

def main():
    # Example usage
    calculator = XExchangeAPRCalculator()
    
    # Example pair and farm addresses (replace with actual addresses)
    pair_address = "erd1qqqqqqqqqqqqqpgqd77fnev2xuqg6q2qpxwnzq2c2h901vk5r4ss7xx68v"
    farm_address = "erd1qqqqqqqqqqqqqpgqd77fnev2xuqg6q2qpxwnzq2c2h901vk5r4ss7xx68v"
    
    # Calculate APRs
    aprs = calculator.get_total_apr(pair_address, farm_address)
    
    # Print results
    print(f"Swap APR: {aprs['swap_apr']:.2f}%")
    print(f"Farm APR: {aprs['farm_apr']:.2f}%")
    print(f"Total APR: {aprs['total_apr']:.2f}%")

if __name__ == "__main__":
    main()