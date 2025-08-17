import { useEffect, useMemo, useRef, useState } from 'react'
import axios from 'axios'
import classNames from 'classnames'

const API_BASE = '/api'

type Tokens = { access: string; refresh: string }

function useAuth() {
	const [tokens, setTokens] = useState<Tokens | null>(null)
	const [username, setUsername] = useState('')

	useEffect(() => {
		const t = localStorage.getItem('tokens')
		if (t) setTokens(JSON.parse(t))
	}, [])

	useEffect(() => {
		if (tokens) localStorage.setItem('tokens', JSON.stringify(tokens))
	}, [tokens])

	const isAuthed = !!tokens?.access
	return { tokens, setTokens, isAuthed, username, setUsername }
}

function Login({ onLoggedIn }: { onLoggedIn: () => void }) {
	const { setTokens, setUsername } = useAuthState()
	const [username, u] = useState('')
	const [password, p] = useState('')
	const [isRegister, setIsRegister] = useState(false)
	const [error, setError] = useState('')

	async function submit(e: React.FormEvent) {
		e.preventDefault()
		setError('')
		try {
			if (isRegister) {
				await axios.post(`${API_BASE}/auth/register/`, { username, password })
			}
			const { data } = await axios.post(`${API_BASE}/auth/token/`, { username, password })
			setTokens(data)
			setUsername(username)
			onLoggedIn()
		} catch (err: any) {
			setError(err?.response?.data?.detail || 'Login failed')
		}
	}

	return (
		<div className="min-h-screen flex items-center justify-center p-6">
			<form onSubmit={submit} className="w-full max-w-md space-y-4 bg-slate-800/60 p-6 rounded-xl border border-slate-700">
				<h1 className="text-2xl font-semibold">SyncParty</h1>
				<p className="text-slate-400">Turn everyone’s phone into a speaker.</p>
				{error && <div className="text-red-400 text-sm">{error}</div>}
				<input className="w-full px-3 py-2 rounded bg-slate-900 border border-slate-700" placeholder="Username" value={username} onChange={e=>u(e.target.value)} />
				<input className="w-full px-3 py-2 rounded bg-slate-900 border border-slate-700" placeholder="Password" type="password" value={password} onChange={e=>p(e.target.value)} />
				<div className="flex items-center justify-between">
					<label className="flex items-center gap-2 text-sm text-slate-400">
						<input type="checkbox" checked={isRegister} onChange={e=>setIsRegister(e.target.checked)} />
						<span>Register new account</span>
					</label>
					<button className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 rounded">{isRegister ? 'Register & Login' : 'Login'}</button>
				</div>
			</form>
		</div>
	)
}

// global auth state via simple singleton
let authState: ReturnType<typeof useAuth> | null = null
function useAuthState() {
	if (!authState) authState = useAuth()
	return authState
}

function useAxios() {
	const { tokens } = useAuthState()
	const instance = useMemo(() => {
		const inst = axios.create()
		inst.interceptors.request.use(config => {
			if (tokens?.access) config.headers.Authorization = `Bearer ${tokens.access}`
			return config
		})
		return inst
	}, [tokens])
	return instance
}

type Party = {
	id: number
	code: string
	name: string
	devices: Device[]
	playback?: { track_uri: string; position_ms: number; is_playing: boolean }
}

type Device = {
	id: number
	label: string
	grid_x: number
	grid_y: number
	is_main_device: boolean
	connected: boolean
}

function PartyDashboard({ party, setParty }: { party: Party | null, setParty: (p: Party|null)=>void }) {
	const api = useAxios()
	const [gridSize, setGridSize] = useState(5)
	const [wsConnected, setWsConnected] = useState(false)
	const wsRef = useRef<WebSocket | null>(null)
	const audioRef = useRef<HTMLAudioElement | null>(null)
	const [trackUrl, setTrackUrl] = useState('')

	useEffect(() => {
		if (!party) return
		const ws = new WebSocket(`ws://localhost:8000/ws/party/${party.code}/`)
		ws.onopen = () => setWsConnected(true)
		ws.onclose = () => setWsConnected(false)
		ws.onmessage = (msg) => {
			try {
				const payload = JSON.parse(msg.data)
				if (payload.event === 'device_update') {
					setParty({ ...party, devices: party.devices.map(d => d.id === payload.data.id ? { ...d, ...payload.data } : d) })
				}
				if (payload.event === 'track' && payload.data?.url) {
					setTrackUrl(payload.data.url)
					if (audioRef.current) {
						audioRef.current.src = payload.data.url
					}
				}
				if (payload.event === 'play') {
					const whenTs = payload.data?.startAtEpochMs as number | undefined
					if (audioRef.current) {
						if (typeof payload.data?.seekMs === 'number') {
							audioRef.current.currentTime = payload.data.seekMs / 1000
						}
						if (whenTs) {
							const delay = whenTs - Date.now()
							if (delay > 10) setTimeout(()=>audioRef.current?.play(), delay)
							else audioRef.current.play()
						} else {
							audioRef.current.play()
						}
					}
				}
				if (payload.event === 'pause') {
					audioRef.current?.pause()
				}
				if (payload.event === 'seek') {
					if (audioRef.current && typeof payload.data?.seekMs === 'number') {
						audioRef.current.currentTime = payload.data.seekMs / 1000
					}
				}
			} catch {}
		}
		wsRef.current = ws
		return () => ws.close()
	}, [party?.code])

	function broadcast(type: string, data: any) {
		wsRef.current?.send(JSON.stringify({ type, data }))
	}

	async function updateDevice(d: Device, coords: {x:number,y:number}) {
		if (!party) return
		const { data } = await api.post(`${API_BASE}/parties/${party.id}/update_device/`, { id: d.id, grid_x: coords.x, grid_y: coords.y })
		broadcast('device_update', data)
		setParty({ ...party, devices: party.devices.map(dd => dd.id === d.id ? data : dd) })
	}

	const grid: Array<Array<Device | null>> = Array.from({ length: gridSize }, () => Array(gridSize).fill(null))
	party?.devices.forEach(d => {
		if (d.grid_x >= 0 && d.grid_x < gridSize && d.grid_y >= 0 && d.grid_y < gridSize) grid[d.grid_y][d.grid_x] = d
	})

	return (
		<div className="p-4 space-y-4">
			<audio ref={audioRef} className="hidden" />
			<div className="flex items-center justify-between">
				<div className="text-xl font-semibold">Party Code: <span className="font-mono">{party?.code}</span></div>
				<div className={classNames('text-sm', wsConnected ? 'text-emerald-400' : 'text-amber-400')}>{wsConnected ? 'Realtime: Connected' : 'Realtime: Connecting...'}</div>
			</div>
			<div className="flex gap-4">
				<div className="flex-1">
					<div className="flex items-center gap-3 mb-2">
						<label>Grid Size</label>
						<select className="bg-slate-800 border border-slate-700 rounded px-2 py-1" value={gridSize} onChange={e=>setGridSize(parseInt(e.target.value))}>
							{[3,4,5,6,7].map(s => <option key={s} value={s}>{s}x{s}</option>)}
						</select>
					</div>
					<div className="grid gap-2" style={{ gridTemplateColumns: `repeat(${gridSize}, minmax(0, 1fr))` }}>
						{Array.from({ length: gridSize * gridSize }).map((_, idx) => {
							const x = idx % gridSize
							const y = Math.floor(idx / gridSize)
							const d = grid[y][x]
							return (
								<div key={idx} className={classNames('aspect-square rounded border border-dashed flex items-center justify-center', d ? 'border-emerald-600 bg-emerald-600/10' : 'border-slate-700')} onClick={()=>{
									if (!d && party?.devices[0]) updateDevice(party.devices[0], {x, y})
								}}>
									{d ? <div className="text-center text-sm">
										<div className="font-medium">{d.label}</div>
										<div className="text-xs text-slate-400">({x},{y})</div>
									</div> : <span className="text-slate-600">+</span>}
								</div>
							)
						})}
					</div>
				</div>
				<div className="w-80 space-y-3">
					<div className="p-3 rounded border border-slate-700 bg-slate-800/50 space-y-2">
						<div className="font-semibold mb-2">Playback</div>
						<input className="w-full px-3 py-2 rounded bg-slate-900 border border-slate-700" placeholder="Paste audio URL (mp3, etc.)" value={trackUrl} onChange={e=>setTrackUrl(e.target.value)} />
						<div className="flex gap-2">
							<button className="px-3 py-1 rounded bg-sky-700" onClick={()=>{ if (trackUrl) { audioRef.current && (audioRef.current.src = trackUrl); broadcast('track',{ url: trackUrl }) } }}>Set Track</button>
							<button className="px-3 py-1 rounded bg-indigo-600" onClick={()=>broadcast('play',{ startAtEpochMs: Date.now() + 300 })}>Play</button>
							<button className="px-3 py-1 rounded bg-slate-700" onClick={()=>broadcast('pause',{})}>Pause</button>
							<button className="px-3 py-1 rounded bg-emerald-700" onClick={()=>broadcast('seek',{ seekMs: (audioRef.current?.currentTime||0)*1000 + 1000 })}>+1s</button>
						</div>
						<p className="text-xs text-slate-400">Tip: Use a short mp3 URL for quick tests. Devices will start in sync using a scheduled start timestamp.</p>
					</div>
				</div>
			</div>
		</div>
	)
}

function Lobby() {
	const api = useAxios()
	const [party, setParty] = useState<Party | null>(null)
	const [name, setName] = useState('My Party')
	const [joinCode, setJoinCode] = useState('')

	async function createParty() {
		const { data } = await api.post(`${API_BASE}/parties/`, { name })
		setParty(data)
		await api.post(`${API_BASE}/parties/${data.id}/join/`, { label: 'Main Device' })
	}

	async function joinByCode() {
		const { data } = await api.post(`${API_BASE}/parties/join-by-code/`, { code: joinCode, label: 'Guest' })
		setParty(data)
	}

	if (party) return <PartyDashboard party={party} setParty={setParty} />
	return (
		<div className="p-6 space-y-6">
			<div className="flex items-center justify-between">
				<h2 className="text-xl font-semibold">Create or Join</h2>
			</div>
			<div className="flex gap-4 flex-wrap">
				<div className="p-4 rounded border border-slate-700 bg-slate-800/60 w-96 space-y-3">
					<div className="font-medium">Create Party</div>
					<input className="w-full px-3 py-2 rounded bg-slate-900 border border-slate-700" value={name} onChange={e=>setName(e.target.value)} />
					<button className="px-4 py-2 rounded bg-indigo-600" onClick={createParty}>Create</button>
				</div>
				<div className="p-4 rounded border border-slate-700 bg-slate-800/60 w-96 space-y-3">
					<div className="font-medium">Join by Code</div>
					<input className="w-full px-3 py-2 rounded bg-slate-900 border border-slate-700" placeholder="ABCD1234" value={joinCode} onChange={e=>setJoinCode(e.target.value)} />
					<button className="px-4 py-2 rounded bg-emerald-600" onClick={joinByCode}>Join</button>
				</div>
			</div>
		</div>
	)
}

export default function App() {
	const auth = useAuthState()
	const [showApp, setShowApp] = useState(auth.isAuthed)
	useEffect(()=>setShowApp(auth.isAuthed), [auth.isAuthed])
	return showApp ? <Lobby /> : <Login onLoggedIn={()=>setShowApp(true)} />
}
