"""
Tests for API endpoints
"""
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_network_stations_structure():
    """Test that /api/network-stations returns correct data structure."""
    response = client.get('/api/network-stations')
    assert response.status_code == 200
    
    data = response.json()
    assert 'stations' in data
    assert isinstance(data['stations'], list)
    
    if len(data['stations']) > 0:
        station = data['stations'][0]
        assert 'id' in station
        assert 'name_en' in station
        assert 'name_ja' in station
        assert isinstance(station['id'], str)
        assert isinstance(station['name_en'], str)
        assert isinstance(station['name_ja'], str)


def test_network_stations_has_data():
    """Test that /api/network-stations returns station data."""
    response = client.get('/api/network-stations')
    data = response.json()
    
    assert len(data['stations']) > 0
    
    # Check for some known stations
    station_names = [s['name_en'] for s in data['stations']]
    assert 'Shibuya' in station_names or 'shibuya' in [s['id'] for s in data['stations']]


def test_network_stations_normalized_ids():
    """Test that station IDs are properly normalized."""
    response = client.get('/api/network-stations')
    data = response.json()
    
    for station in data['stations']:
        # IDs should be lowercase and use hyphens
        assert station['id'] == station['id'].lower()
        assert ' ' not in station['id']


def test_route_compare_missing_origin():
    """Test that missing origin returns error message."""
    response = client.get('/route-compare?destination=Tokorozawa')
    assert response.status_code == 200
    assert b'Please enter an origin station' in response.content


def test_route_compare_missing_destination():
    """Test that missing destination returns error message."""
    response = client.get('/route-compare?origin=Shibuya')
    assert response.status_code == 200
    assert b'Please enter a destination station' in response.content


def test_route_compare_invalid_station():
    """Test that invalid station name returns error message."""
    response = client.get('/route-compare?origin=InvalidStation&destination=Shibuya')
    assert response.status_code == 200
    assert b'not found' in response.content


def test_route_compare_same_station():
    """Test that same origin and destination returns error message."""
    response = client.get('/route-compare?origin=Shibuya&destination=Shibuya')
    assert response.status_code == 200
    assert b'must be different' in response.content


def test_route_compare_valid_stations():
    """Test that valid station pair returns routes."""
    response = client.get('/route-compare?origin=Shibuya&destination=Tokorozawa')
    assert response.status_code == 200
    # Should not have error message
    assert b'Please enter' not in response.content or b'not found' not in response.content
