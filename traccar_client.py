"""
Traccar OsmAnd Protocol Client

Provides functionality to send device position data to a Traccar server
using the OsmAnd protocol.

Full specification: https://www.traccar.org/osmand/
"""

import aiohttp
from typing import Optional
from datetime import datetime
from urllib.parse import urlencode


async def send_osmand_position(
    traccar_url: str,
    device_id: str,
    lat: float,
    lon: float,
    *,
    timestamp: Optional[datetime] = None,
    speed: Optional[float] = None,
    bearing: Optional[float] = None,
    altitude: Optional[float] = None,
    accuracy: Optional[float] = None,
    hdop: Optional[float] = None,
    battery: Optional[float] = None,
    charge: Optional[bool] = None,
    valid: Optional[bool] = None,
    driver_unique_id: Optional[str] = None,
    session: Optional[aiohttp.ClientSession] = None,
    timeout: int = 30,
    **custom_attributes
) -> bool:
    """
    Send position data to Traccar server using OsmAnd protocol.

    Args:
        traccar_url: Base URL of the Traccar server (e.g., 'http://localhost:5055')
        device_id: Unique device identifier
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees
        timestamp: Position timestamp (defaults to current time if not provided)
        speed: Speed in knots
        bearing: Direction of movement in degrees (0-360)
        altitude: Altitude in meters
        accuracy: Position accuracy in meters
        hdop: Horizontal dilution of precision
        battery: Battery level (0-100)
        charge: Whether device is charging (True/False)
        valid: Whether the GPS position is valid
        driver_unique_id: Driver identifier
        session: Optional aiohttp.ClientSession (will create one if not provided)
        timeout: Request timeout in seconds
        **custom_attributes: Additional custom attributes to send with the position

    Returns:
        bool: True if request was successful, False otherwise

    Raises:
        ValueError: If required parameters are invalid
        aiohttp.ClientError: If network request fails

    Examples:
        >>> # Basic usage with required parameters only
        >>> await send_osmand_position(
        ...     traccar_url="http://localhost:5055",
        ...     device_id="robot-vacuum-001",
        ...     lat=37.7749,
        ...     lon=-122.4194
        ... )

        >>> # With optional parameters
        >>> await send_osmand_position(
        ...     traccar_url="http://localhost:5055",
        ...     device_id="robot-vacuum-001",
        ...     lat=37.7749,
        ...     lon=-122.4194,
        ...     speed=5.2,
        ...     bearing=180,
        ...     altitude=10,
        ...     battery=85,
        ...     charge=True
        ... )

        >>> # With custom attributes
        >>> await send_osmand_position(
        ...     traccar_url="http://localhost:5055",
        ...     device_id="robot-vacuum-001",
        ...     lat=37.7749,
        ...     lon=-122.4194,
        ...     cleaning_mode="auto",
        ...     room="living_room"
        ... )

        >>> # Reusing a session for multiple requests
        >>> async with aiohttp.ClientSession() as session:
        ...     await send_osmand_position(
        ...         traccar_url="http://localhost:5055",
        ...         device_id="robot-vacuum-001",
        ...         lat=37.7749,
        ...         lon=-122.4194,
        ...         session=session
        ...     )
    """
    # Validate required parameters
    if not device_id:
        raise ValueError("device_id is required")
    if not isinstance(lat, (int, float)) or not -90 <= lat <= 90:
        raise ValueError("lat must be a number between -90 and 90")
    if not isinstance(lon, (int, float)) or not -180 <= lon <= 180:
        raise ValueError("lon must be a number between -180 and 180")

    # Build parameters dictionary
    params = {
        "id": device_id,
        "lat": lat,
        "lon": lon,
    }

    # Add optional parameters if provided
    if timestamp is not None:
        # Convert datetime to Unix timestamp (milliseconds)
        params["timestamp"] = int(timestamp.timestamp() * 1000)

    if speed is not None:
        params["speed"] = speed

    if bearing is not None:
        params["bearing"] = bearing

    if altitude is not None:
        params["altitude"] = altitude

    if accuracy is not None:
        params["accuracy"] = accuracy

    if hdop is not None:
        params["hdop"] = hdop

    if battery is not None:
        params["batt"] = battery

    if charge is not None:
        params["charge"] = "true" if charge else "false"

    if valid is not None:
        params["valid"] = "true" if valid else "false"

    if driver_unique_id is not None:
        params["driverUniqueId"] = driver_unique_id

    # Add any custom attributes
    params.update(custom_attributes)

    # Construct the full URL
    url = traccar_url.rstrip('/')

    # Determine if we need to manage the session
    close_session = False
    if session is None:
        session = aiohttp.ClientSession()
        close_session = True

    try:
        # Send GET request to Traccar
        async with session.get(
            url,
            params=params,
            timeout=aiohttp.ClientTimeout(total=timeout)
        ) as response:
            # Traccar returns 200 OK on success
            success = response.status == 200

            if not success:
                # Log the error response for debugging
                error_text = await response.text()
                raise aiohttp.ClientError(
                    f"Traccar request failed with status {response.status}: {error_text}"
                )
            else:
                # Log the success response for debugging
                print(f"Traccar request succeeded with status {response.status}")

            return success

    except Exception as e:
        raise
    finally:
        if close_session:
            await session.close()
