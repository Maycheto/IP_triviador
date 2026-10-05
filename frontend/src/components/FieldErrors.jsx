function FieldErrors({ errors }) {
  if (!errors || errors.length === 0) {
    return null
  }

  return (
    <ul className="field-errors">
      {errors.map((message) => (
        <li key={message}>{message}</li>
      ))}
    </ul>
  )
}

export default FieldErrors
