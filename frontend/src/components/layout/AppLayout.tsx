import { Outlet, useLocation } from "react-router-dom";
import BottomNav from "./BottomNav";

export default function AppLayout() {
  const inbox = useLocation().pathname === "/inbox";
  return (
    <div className={inbox ? "flex h-dvh flex-col overflow-hidden" : "min-h-screen pb-24"}>
      <Outlet />
      <BottomNav embedded={inbox} />
    </div>
  );
}
