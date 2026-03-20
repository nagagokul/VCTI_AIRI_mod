import { Navigate } from "react-router-dom"

type Props = {
  user: any
  children: React.ReactNode
}

export default function ProtectedRoute({ user, children }: Props) {
  if (!user) {
    return <Navigate to="/" />
  }

  return <>{children}</>
}