import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { updateMe } from '../api.js'
import { useAuth } from '../AuthContext.jsx'
import Avatar from '../components/Avatar.jsx'
import FieldErrors from '../components/FieldErrors.jsx'

const AVATAR_KEYS = ['knight-1', 'knight-2', 'knight-3', 'knight-4']

function ProfilePage() {
  const { user, setUser, logout } = useAuth()
  const navigate = useNavigate()

  const [nickname, setNickname] = useState(user.profile.nickname)
  const [avatarKey, setAvatarKey] = useState(user.profile.avatar_key)
  const [errors, setErrors] = useState({})
  const [message, setMessage] = useState('')
  const [saving, setSaving] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setErrors({})
    setMessage('')
    setSaving(true)

    try {
      const data = await updateMe({ nickname, avatar_key: avatarKey })
      setUser(data)
      setMessage('Profile saved.')
    } catch (error) {
      setErrors(error.data?.errors || { non_field_errors: ['Something went wrong. Try again.'] })
    } finally {
      setSaving(false)
    }
  }

  async function handleLogout() {
    try {
      await logout()
      navigate('/login')
    } catch (error) {
      setErrors(error.data?.errors || { non_field_errors: ['Logout failed. Try again.'] })
    }
  }

  return (
    <>
      <h1>Profile</h1>

      <div className="profile-info">
        <Avatar avatarKey={user.profile.avatar_key} size={80} />
        <div>
          <p>
            <strong>Username:</strong> {user.username}
          </p>
          <p>
            <strong>Email:</strong> {user.email}
          </p>
          <p>
            <strong>Nickname:</strong> {user.profile.nickname}
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <h2>Edit profile</h2>

        <FieldErrors errors={errors.non_field_errors} />
        <FieldErrors errors={errors.detail} />

        <div>
          <label htmlFor="nickname">Nickname</label>
          <input id="nickname" value={nickname} onChange={(e) => setNickname(e.target.value)} />
          <FieldErrors errors={errors.nickname} />
        </div>

        <div>
          <p>Avatar</p>
          <div className="avatar-picker">
            {AVATAR_KEYS.map((key) => (
              <button
                key={key}
                type="button"
                className={key === avatarKey ? 'avatar-card selected' : 'avatar-card'}
                onClick={() => setAvatarKey(key)}
              >
                <Avatar avatarKey={key} />
                <span>{key}</span>
              </button>
            ))}
          </div>
          <FieldErrors errors={errors.avatar_key} />
        </div>

        <button type="submit" disabled={saving}>
          {saving ? 'Saving...' : 'Save'}
        </button>
        {message && <p>{message}</p>}
      </form>

      <button type="button" onClick={handleLogout}>
        Logout
      </button>
    </>
  )
}

export default ProfilePage
