import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { register } from '../api.js'
import { useAuth } from '../AuthContext.jsx'
import FieldErrors from '../components/FieldErrors.jsx'

const FIELDS = [
  { name: 'username', label: 'Username', type: 'text', autoComplete: 'username' },
  { name: 'email', label: 'Email', type: 'email', autoComplete: 'email' },
  { name: 'nickname', label: 'Nickname', type: 'text', autoComplete: 'nickname' },
  { name: 'password', label: 'Password', type: 'password', autoComplete: 'new-password' },
  { name: 'password_confirm', label: 'Confirm password', type: 'password', autoComplete: 'new-password' },
]

function RegisterPage() {
  const { login } = useAuth()
  const navigate = useNavigate()

  const [form, setForm] = useState({
    username: '',
    email: '',
    nickname: '',
    password: '',
    password_confirm: '',
  })
  const [errors, setErrors] = useState({})
  const [submitting, setSubmitting] = useState(false)

  function handleChange(event) {
    setForm({ ...form, [event.target.name]: event.target.value })
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setErrors({})
    setSubmitting(true)

    try {
      await register(form)
      // register does not start a session, so log in with the same credentials
      await login(form.username, form.password)
      navigate('/profile')
    } catch (error) {
      setErrors(error.data?.errors || { non_field_errors: ['Something went wrong. Try again.'] })
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <>
      <h1>Register</h1>

      <form onSubmit={handleSubmit}>
        <FieldErrors errors={errors.non_field_errors} />
        <FieldErrors errors={errors.detail} />

        {FIELDS.map((field) => (
          <div key={field.name}>
            <label htmlFor={field.name}>{field.label}</label>
            <input
              id={field.name}
              name={field.name}
              type={field.type}
              value={form[field.name]}
              onChange={handleChange}
              autoComplete={field.autoComplete}
            />
            <FieldErrors errors={errors[field.name]} />
          </div>
        ))}

        <button type="submit" disabled={submitting}>
          {submitting ? 'Registering...' : 'Register'}
        </button>
      </form>

      <p>
        Already have an account? <Link to="/login">Login</Link>
      </p>
    </>
  )
}

export default RegisterPage
