import { useState } from "react";
import { useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";
import { loginSuccess } from "../store/slices/userSlice";

export default function Login() {
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();
    setIsLoading(true);
    
    // Simulation d'un appel API avec délai pour l'animation
    setTimeout(() => {
      dispatch(loginSuccess({ user: { identifier }, token: "fake-jwt-token" }));
      setIsLoading(false);
      navigate("/products");
    }, 1000);
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1 className="auth-logo">Faso-Commerce</h1>
          <p className="auth-subtitle">Accédez à votre espace sécurisé</p>
        </div>
        
        <form onSubmit={handleLogin}>
          <div className="input-group">
            <label className="input-label">Email ou Numéro de Téléphone</label>
            <input 
              type="text" 
              className="auth-input"
              placeholder="ex: +226 70000000" 
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
        </form>
      </div>
    </div>
  );
}
