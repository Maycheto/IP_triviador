import { useAuth } from '../AuthContext.jsx'

function ProfilePage() {
  const { user } = useAuth()

  return (
    <>
      <h1>Profile</h1>
      <p>Logged in as {user.username}</p>
    </>
  )
}

export default ProfilePage
