import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { registerUser, verifyOtp } from "../api/users";

export default function Register() {
  const [step, setStep] = useState(1); // 1 = Details, 2 = OTP
  const [phoneNumber, setPhoneNumber] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");
  const [otpCode, setOtpCode] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [successMsg, setSuccessMsg] = useState("");
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
    if (password !== passwordConfirm) {
      setErrorMsg("Les mots de passe ne correspondent pas.");
      return;
    }

    setIsLoading(true);
    setErrorMsg("");
    try {
      await registerUser({ 
        phone_number: phoneNumber, 
        email: email,
        password: password,
        password_confirm: passwordConfirm
      });
      setSuccessMsg("Un code OTP a été envoyé par SMS.");
      setStep(2);
    } catch (err) {
      console.error(err);
      const apiErrors = err.response?.data;
      if (apiErrors && typeof apiErrors === 'object') {
        const errorDetail = JSON.stringify(apiErrors);
        setErrorMsg(`Détail de l'erreur : ${errorDetail}`);
        console.error("Détail complet de l'erreur API :", apiErrors);
      } else {
        setErrorMsg("Erreur lors de l'inscription. Vérifiez vos informations.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerifyOtp = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMsg("");
    try {
      await verifyOtp(phoneNumber, otpCode, "registration");
      const params = new URLSearchParams(window.location.search);
      const redirect = params.get("redirect");
      navigate(redirect ? `/login?redirect=${encodeURIComponent(redirect)}` : "/login");
    } catch (err) {
      console.error(err);
      setErrorMsg("Code OTP invalide ou expiré.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1 className="auth-logo">Créer un compte</h1>
          <p className="auth-subtitle">Rejoignez Faso-Commerce</p>
        </div>

        {errorMsg && (
          <div style={{ padding: '10px', backgroundColor: '#ffd2d2', color: '#d8000c', borderRadius: '8px', marginBottom: '15px', fontSize: '0.9rem', textAlign: 'center' }}>
            {errorMsg}
          </div>
        )}
        
        {successMsg && step === 2 && (
          <div style={{ padding: '10px', backgroundColor: '#d4edda', color: '#155724', borderRadius: '8px', marginBottom: '15px', fontSize: '0.9rem', textAlign: 'center' }}>
            {successMsg}
          </div>
        )}

        {step === 1 ? (
          <form onSubmit={handleRegister}>
            <div className="input-group">
              <label className="input-label">Numéro de Téléphone</label>
              <input
                type="text"
                className="auth-input"
                placeholder="ex: +226 70000000"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                required
              />
            </div>

            <div className="input-group">
              <label className="input-label">Adresse E-mail</label>
              <input
                type="email"
                className="auth-input"
                placeholder="votre@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
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

            <div className="input-group">
              <label className="input-label">Confirmer le mot de passe</label>
              <input
                type="password"
                className="auth-input"
                placeholder="••••••••"
                value={passwordConfirm}
                onChange={(e) => setPasswordConfirm(e.target.value)}
                required
              />
            </div>

            <button type="submit" className="auth-button" disabled={isLoading}>
              {isLoading ? "Veuillez patienter..." : "S'inscrire"}
            </button>
            <div style={{ marginTop: "1.5rem", textAlign: "center", color: "var(--text-muted)", fontSize: "0.9rem" }}>
              Déjà un compte ? <Link to={`/login${window.location.search}`} style={{ color: "var(--primary)", textDecoration: "none" }}>Se connecter</Link>
            </div>
          </form>
        ) : (
          <form onSubmit={handleVerifyOtp}>
            <div className="input-group">
              <label className="input-label">Code OTP de vérification</label>
              <input
                type="text"
                className="auth-input"
                placeholder="Entrez le code à 6 chiffres"
                value={otpCode}
                onChange={(e) => setOtpCode(e.target.value)}
                required
              />
            </div>
            <button type="submit" className="auth-button" disabled={isLoading}>
              {isLoading ? "Vérification..." : "Valider mon compte"}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
