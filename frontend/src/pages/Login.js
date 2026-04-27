import { useState } from "react";
import { useDispatch } from "react-redux";
import { useNavigate, Link } from "react-router-dom";
import { loginSuccess } from "../store/slices/userSlice";
import { loginUser } from "../api/users";

export default function Login() {
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMsg("");
    
    try {
      const data = await loginUser({ phone_number: identifier, password: password });
      
      const params = new URLSearchParams(window.location.search);
      const redirectPath = params.get("redirect") || "/products";
      
      dispatch(loginSuccess({ 
        user: data.user, 
        token: data.access 
      }));
      
      navigate(redirectPath);
    } catch (err) {
      console.error("Login Error:", err.response?.data || err.message);
      const apiErrors = err.response?.data;
      if (apiErrors && typeof apiErrors === 'object' && apiErrors.detail) {
        setErrorMsg(apiErrors.detail);
      } else {
        setErrorMsg("Identifiants incorrects ou session invalide. Veuillez vider votre cache.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1 className="auth-logo">Faso-Commerce</h1>
          <p className="auth-subtitle">Accédez à votre espace sécurisé</p>
        </div>
        
        {errorMsg && (
          <div style={{ padding: '10px', backgroundColor: '#ffd2d2', color: '#d8000c', borderRadius: '8px', marginBottom: '15px', fontSize: '0.9rem', textAlign: 'center' }}>
            {errorMsg}
          </div>
        )}

        <form onSubmit={handleLogin}>
          <div className="input-group">
            <label className="input-label">Numéro de Téléphone / Email</label>
            <input 
              type="text" 
              className="auth-input"
              placeholder="Téléphone ou Email" 
              value={identifier} 
              onChange={(e) => setIdentifier(e.target.value)} 
              required
            />
          </div>
          
          <div className="input-group">
            <label className="input-label">Mot de passe</label>
            <input 
              type="password" 
              className="auth-input"
              placeholder="••••••••" 
              value={password} 
              onChange={(e) => setPassword(e.target.value)} 
              required
            />
          </div>
          
          <button type="submit" className="auth-button" disabled={isLoading}>
            {isLoading ? "Connexion en cours..." : "Se connecter"}
          </button>
          
          <div style={{ marginTop: "1.5rem", textAlign: "center", color: "var(--text-muted)", fontSize: "0.9rem" }}>
            Pas encore de compte ? <Link to={`/register${window.location.search}`} style={{ color: "var(--primary)", textDecoration: "none" }}>S'inscrire</Link>
          </div>
        </form>
      </div>
    </div>
  );
}
