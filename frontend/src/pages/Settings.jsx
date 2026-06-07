import API from "../api/api";
import { useEffect, useState } from "react";
import "./Settings.css";
function Settings() {
  const [settings, setSettings] = useState({
    universe: "us_largecap",
    scanMode: "fast",
    scanLimit: 50,
    fast: 5,
    slow: 30,
    rsiSell: 70,
    stopLoss: 0.03,
  });
  const [saving, setSaving] = useState(false);
  useEffect(() => {
    API.get("/settings")
      .then((res) => {
        setSettings(res.data);
      })
      .catch(console.error);
  }, []);
  async function updateSetting(key, value) {
    const updated = { ...settings, [key]: value };
    setSettings(updated);
    setSaving(true);
    try {
      const payload = {
        universe: updated.universe,
        scan_mode: updated.scanMode,
        scan_limit: updated.scanLimit,
        fast: Number(updated.fast),
        slow: Number(updated.slow),
        rsi_sell: Number(updated.rsiSell),
        stop_loss: Number(updated.stopLoss),
      };
      const res = await API.put("/settings", payload);
      setSettings(res.data);
    } catch (err) {
      console.error(err);
      alert("Failed to save settings.");
    }
    setSaving(false);
  }
  return (
    <div className="settings-page">
      <section className="settings-hero">
        <div>
          <p className="eyebrow">QUANTOS</p>
          <h1>Settings</h1>
          <p className="muted">
            Control how your discovery engine scans, scores, and ranks stocks.
          </p>
        </div>
        <div className="settings-status">
          {saving ? "Saving..." : "Saved to database"}
        </div>
      </section>
      <section className="settings-card">
        <div className="settings-card-header">
          <div>
            <p className="eyebrow">DISCOVERY</p>
            <h2>Market Scan Defaults</h2>
          </div>
        </div>
        <div className="settings-grid">
          <div className="setting-field">
            <label>Default Universe</label>
            <select
              value={settings.universe}
              onChange={(e) => updateSetting("universe", e.target.value)}
            >
              <option value="watchlist">My Watchlist</option>
              <option value="us_largecap">US Large Cap</option>
              <option value="sti30">Singapore STI30</option>
            </select>
          </div>
          <div className="setting-field">
            <label>Scan Mode</label>
            <select
              value={settings.scanMode}
              onChange={(e) => updateSetting("scanMode", e.target.value)}
            >
              <option value="fast">Fast Scan</option>
              <option value="deep">Deep Scan</option>
            </select>
          </div>
          <div className="setting-field">
            <label>Stocks To Scan</label>
            <select
              value={settings.scanLimit}
              onChange={(e) =>
                updateSetting("scanLimit", Number(e.target.value))
              }
            >
              <option value={25}>25</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
              <option value={250}>250</option>
              <option value={500}>500</option>
            </select>
          </div>
        </div>
      </section>
      <section className="settings-card">
        <div className="settings-card-header">
          <div>
            <p className="eyebrow">STRATEGY</p>
            <h2>Technical Parameters</h2>
          </div>
        </div>
        <div className="settings-grid">
          <div className="setting-field">
            <label>Fast SMA</label>
            <input
              value={settings.fast ?? ""}
              onChange={(e) => updateSetting("fast", Number(e.target.value))}
            />
          </div>
          <div className="setting-field">
            <label>Slow SMA</label>
            <input
              value={settings.slow ?? ""}
              onChange={(e) => updateSetting("slow", Number(e.target.value))}
            />
          </div>
          <div className="setting-field">
            <label>RSI Exit</label>
            <input
              value={settings.rsiSell ?? ""}
              onChange={(e) => updateSetting("rsiSell", Number(e.target.value))}
            />
          </div>
          <div className="setting-field">
            <label>Stop Loss</label>
            <input
              value={settings.stopLoss ?? ""}
              onChange={(e) =>
                updateSetting("stopLoss", Number(e.target.value))
              }
            />
          </div>
        </div>
      </section>
    </div>
  );
}
export default Settings;