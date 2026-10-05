const AVATAR_COLORS = {
  'knight-1': '#c75b7a',
  'knight-2': '#6b3a6e',
  'knight-3': '#5f7d5a',
  'knight-4': '#b8893f',
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
