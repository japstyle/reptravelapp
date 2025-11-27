#!/usr/bin/env python3
"""
Quick test to verify the transfer-aware scoring system works correctly.
"""

from route_finder import find_routes
from scoring import score_route

def test_shibuya_to_tokorozawa():
    """Test the main use case: Shibuya to Tokorozawa."""
    print("=" * 60)
    print("Testing: Shibuya → Tokorozawa")
    print("=" * 60)
    
    routes = find_routes("Shibuya", "Tokorozawa")
    
    if not routes:
        print("❌ No routes found!")
        return False
    
    print(f"\nFound {len(routes)} route alternatives:\n")
    
    scored_routes = []
    for route in routes:
        score = score_route(route)
        scored_routes.append({
            'name': route.get('name'),
            'score': score,
            'segments': route['segments']
        })
    
    # Sort by total felt time
    scored_routes.sort(key=lambda x: x['score']['total_seconds'])
    
    for i, route in enumerate(scored_routes, 1):
        total_min = route['score']['total_seconds'] / 60
        actual_ride_min = sum(s['duration_seconds'] for s in route['segments']) / 60
        
        print(f"{i}. {route['name']}")
        print(f"   Felt time: {total_min:.1f} min (Actual: {actual_ride_min:.1f} min)")
        
        # Show transfer penalties
        for j, seg in enumerate(route['segments']):
            if seg.get('is_transfer'):
                transfer_penalty = route['score']['segments'][j]['transfer_penalty']
                print(f"   Transfer at {seg['from_station']}: +{transfer_penalty/60:.1f} min penalty")
        
        print()
    
    # Verify the best route
    best_route = scored_routes[0]
    print(f"✅ Best route: {best_route['name']}")
    print(f"   (Felt time: {best_route['score']['total_seconds']/60:.1f} min)")
    
    # Check if Nerima route wins (it should due to easier transfer)
    if "Nerima" in best_route['name']:
        print("✅ Nerima route correctly identified as best due to easy transfer!")
        return True
    else:
        print("⚠️  Expected Nerima route to be best, but got:", best_route['name'])
        return False

def test_transfer_database_lookup():
    """Test that transfer database lookups work."""
    print("\n" + "=" * 60)
    print("Testing: Transfer Database Lookups")
    print("=" * 60 + "\n")
    
    from scoring import find_transfer_data, calculate_transfer_time
    
    # Test Ikebukuro transfer (should be complex)
    ikebukuro = find_transfer_data("Ikebukuro", "TokyoMetro.Fukutoshin", "Seibu.Ikebukuro")
    if ikebukuro:
        time = calculate_transfer_time(ikebukuro)
        print(f"✅ Ikebukuro transfer (Fukutoshin → Seibu): {time/60:.1f} min")
        print(f"   Distance: {ikebukuro['distance_m']}m, Floors: {ikebukuro['floors']}, Crowd: {ikebukuro['crowd_factor']}x")
    else:
        print("❌ Ikebukuro transfer not found!")
        return False
    
    # Test Nerima transfer (should be easy)
    nerima = find_transfer_data("Nerima", "TokyoMetro.Fukutoshin", "Seibu.Ikebukuro")
    if nerima:
        time = calculate_transfer_time(nerima)
        print(f"✅ Nerima transfer (Fukutoshin → Seibu): {time/60:.1f} min")
        print(f"   Distance: {nerima['distance_m']}m, Floors: {nerima['floors']}, Platform: {nerima['platform_type']}")
    else:
        print("❌ Nerima transfer not found!")
        return False
    
    # Verify Nerima is easier than Ikebukuro
    ikebukuro_time = calculate_transfer_time(ikebukuro)
    nerima_time = calculate_transfer_time(nerima)
    
    print(f"\n✅ Transfer comparison:")
    print(f"   Ikebukuro: {ikebukuro_time/60:.1f} min")
    print(f"   Nerima: {nerima_time/60:.1f} min")
    print(f"   Difference: {(ikebukuro_time - nerima_time)/60:.1f} min")
    
    if nerima_time < ikebukuro_time:
        print("✅ Nerima is correctly scored as easier!")
        return True
    else:
        print("❌ Scoring error: Nerima should be easier than Ikebukuro")
        return False

def main():
    print("\n🧪 Transfer-Aware Route Scoring Test Suite\n")
    
    tests_passed = 0
    tests_total = 2
    
    if test_transfer_database_lookup():
        tests_passed += 1
    
    if test_shibuya_to_tokorozawa():
        tests_passed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {tests_passed}/{tests_total} tests passed")
    print("=" * 60)
    
    if tests_passed == tests_total:
        print("\n✅ All tests passed! The app is working correctly.")
    else:
        print(f"\n⚠️  {tests_total - tests_passed} test(s) failed. Check the output above.")

if __name__ == "__main__":
    main()
