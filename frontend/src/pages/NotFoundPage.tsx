import { Link } from "react-router-dom";
import { EmptyState } from "../components/common/States";
import Navbar from "../components/layout/Navbar";

export default function NotFoundPage() {
  return (
    <>
      <Navbar />
      <EmptyState title="404 — page not found">
        <Link to="/discover" className="text-cyan-300 hover:underline">
          Back to Discover
        </Link>
      </EmptyState>
    </>
  );
}
