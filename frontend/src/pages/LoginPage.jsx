import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../AuthContext.jsx'
import FieldErrors from '../components/FieldErrors.jsx'

function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()

  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [errors, setErrors] = useState({})
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setErrors({})
    setSubmitting(true)

    try {
      await login(username, password)
      navigate('/profile')
    } catch (error) {
      setErrors(error.data?.errors || { non_field_errors: ['Something went wrong. Try again.'] })
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <>
      <h1>Login</h1>

      <form onSubmit={handleSubmit}>
        <FieldErrors errors={errors.non_field_errors} />
        <FieldErrors errors={errors.detail} />

        <div>
          <label htmlFor="username">Username</label>
          <input
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoComplete="username"
          />
          <FieldErrors errors={errors.username} />
        </div>

        <div>
          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
          />
          <FieldErrors errors={errors.password} />
        </div>

        <button type="submit" disabled={submitting}>
          {submitting ? 'Logging in...' : 'Login'}
        </button>
      </form>

      <p>
        No account? <Link to="/register">Register</Link>
      </p>
    </>
  )
}

export default LoginPage
