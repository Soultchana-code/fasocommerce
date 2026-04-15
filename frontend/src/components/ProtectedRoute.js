import { Navigate } from "react-router-dom";
import { useSelector } from "react-redux";

export default function ProtectedRoute({ children }) {
  const token = useSelector((state) => state.user.token);
  return token ? children : <Navigate to="/login" />;
}
