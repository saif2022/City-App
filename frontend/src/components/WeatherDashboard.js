import React, { useState } from "react";

import "../App.css";

function WeatherApp() {
  const [city, setCity] = useState("");
  const [weatherData, setWeatherData] = useState(null);
  const [error, setError] = useState("");

  const fetchWeatherData = async () => {
    setError(""); // Clear previous errors
    setWeatherData(null); // Clear previous data

    try {
      const response = await fetch("http://localhost:5000/weather", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ city }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Server error");
      }

      const data = await response.json();
      setWeatherData(data);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div>
      <h1>Weather Dashboard</h1>
      <input
        type="text"
        placeholder="Enter city name"
        value={city}
        onChange={(e) => setCity(e.target.value)}
      />
      <button onClick={fetchWeatherData}>Get Weather</button>

      {error && <p style={{ color: "red" }}>Error: {error}</p>}

      {weatherData && (
        <div>
          <h2>Weather in the {city}</h2>
          <p>Temperature: {weatherData.weather.main.temp}°F</p>
          <p>Feels Like: {weatherData.weather.main.feels_like}°F</p>
          <p>Conditions: {weatherData.weather.weather[0].description}</p>
          <h3>Forecast:</h3>
          <ul>
            {weatherData.forecast.list.map((forecast, index) => (
              <li key={index}>
                Date: {forecast.dt_txt}, Temp: {forecast.main.temp}°F
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default WeatherApp;
