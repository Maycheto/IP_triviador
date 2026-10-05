const AVATAR_COLORS = {
  'knight-1': '#c62828',
  'knight-2': '#1565c0',
  'knight-3': '#2e7d32',
  'knight-4': '#f9a825',
}

function Avatar({ avatarKey, size = 64 }) {
  return (
    <div
      className="avatar"
      style={{
        backgroundColor: AVATAR_COLORS[avatarKey] || '#777',
        width: size,
        height: size,
        fontSize: size / 2,
      }}
    >
      ♞
    </div>
  )
}

export default Avatar
