---
name: voice-chat
description: Build or debug MogMatch's 1:1 voice calls between matched users using browser WebRTC via Blazor JS interop, with signaling over the SignalR ChatHub. Use for the call button, voice.js, mute/hang up, "no audio", "call won't connect", or screen share.
---

# Voice Chat (WebRTC + SignalR signaling)

Stretch feature — build after text chat works. Files: `wwwroot/js/voice.js`, `Components/Shared/CallButton.razor`, signaling methods on `Hubs/ChatHub.cs`.

## How it works
1. Caller clicks **Call** → JS gets the mic (`getUserMedia`), creates an `RTCPeerConnection`, makes an **offer**.
2. The offer, the **answer**, and **ICE candidates** are relayed between the two browsers through `ChatHub` (the "signaling").
3. Once connected, audio flows **peer-to-peer** — the server never touches it.

## Hub additions
```csharp
public async Task SendSignal(Guid matchId, string type, string payload)   // type: offer | answer | ice | hangup
{
    if (!await chat.IsMemberAsync(matchId, UserId)) throw new HubException("Not your match");
    await Clients.OthersInGroup($"match-{matchId}").SendAsync("Signal", type, payload);
}
```

## voice.js (browser connects to the hub directly)
Load the SignalR JS client in `App.razor`:
`<script src="https://cdnjs.cloudflare.com/ajax/libs/microsoft-signalr/8.0.7/signalr.min.js"></script>`
```js
let hub, pc, localStream, matchId;
const ICE = { iceServers: [{ urls: "stun:stun.l.google.com:19302" }] };

export async function init(id) {
  matchId = id;
  hub = new signalR.HubConnectionBuilder().withUrl("/hubs/chat").withAutomaticReconnect().build();
  hub.on("Signal", onSignal);
  await hub.start();                         // same-origin → auth cookie sent automatically
  await hub.invoke("JoinMatch", matchId);
}

async function setupPeer() {
  pc = new RTCPeerConnection(ICE);
  localStream = await navigator.mediaDevices.getUserMedia({ audio: true });
  localStream.getTracks().forEach(t => pc.addTrack(t, localStream));
  pc.onicecandidate = e => e.candidate && hub.invoke("SendSignal", matchId, "ice", JSON.stringify(e.candidate));
  pc.ontrack = e => { document.getElementById("remote-audio").srcObject = e.streams[0]; };
}

export async function call() {
  await setupPeer();
  const offer = await pc.createOffer();
  await pc.setLocalDescription(offer);
  await hub.invoke("SendSignal", matchId, "offer", JSON.stringify(offer));
}

async function onSignal(type, payload) {
  if (type === "offer") {
    await setupPeer();                       // stretch: show "Incoming call — accept?" first
    await pc.setRemoteDescription(JSON.parse(payload));
    const answer = await pc.createAnswer();
    await pc.setLocalDescription(answer);
    await hub.invoke("SendSignal", matchId, "answer", JSON.stringify(answer));
  } else if (type === "answer") {
    await pc.setRemoteDescription(JSON.parse(payload));
  } else if (type === "ice" && pc) {
    await pc.addIceCandidate(JSON.parse(payload));
  } else if (type === "hangup") {
    cleanup();
  }
}

export function setMuted(muted) { localStream?.getAudioTracks().forEach(t => t.enabled = !muted); }
export async function hangUp() { await hub.invoke("SendSignal", matchId, "hangup", ""); cleanup(); }
function cleanup() { localStream?.getTracks().forEach(t => t.stop()); pc?.close(); pc = null; }
```

## CallButton.razor
```razor
@inject IJSRuntime JS
@implements IAsyncDisposable
@rendermode InteractiveServer

<audio id="remote-audio" autoplay></audio>
@if (!inCall) { <button class="btn btn-primary" @onclick="StartCall">📞 Call</button> }
else
{
    <button class="btn btn-secondary" @onclick="ToggleMute">@(muted ? "Unmute" : "Mute")</button>
    <button class="btn btn-danger" @onclick="HangUp">Hang up</button>
}

@code {
    [Parameter] public Guid MatchId { get; set; }
    private IJSObjectReference? voice;
    private bool inCall, muted;

    protected override async Task OnAfterRenderAsync(bool firstRender)
    {
        if (!firstRender) return;                            // JS interop only works after render
        voice = await JS.InvokeAsync<IJSObjectReference>("import", "./js/voice.js");
        await voice.InvokeVoidAsync("init", MatchId);
    }

    private async Task StartCall() { await voice!.InvokeVoidAsync("call"); inCall = true; }
    private async Task ToggleMute() { muted = !muted; await voice!.InvokeVoidAsync("setMuted", muted); }
    private async Task HangUp() { await voice!.InvokeVoidAsync("hangUp"); inCall = false; }
    public async ValueTask DisposeAsync() { if (voice is not null) await voice.DisposeAsync(); }
}
```

## Testing
- Use **two different browsers** (e.g. Chrome + Edge) logged in as the two matched users — the same browser shares cookies.
- Mic access requires **HTTPS or localhost**.
- Use headphones, or you'll get echo.

## Troubleshooting
| Symptom | Likely cause |
|---|---|
| `NotAllowedError` | mic permission denied, or page isn't HTTPS |
| Connects on same Wi-Fi, fails across networks | strict NAT — needs a TURN server (stretch: free tier from Metered/Twilio) |
| No sound but "connected" | `<audio>` missing `autoplay`, or browser blocked autoplay — play after a click |
| `JoinMatch` 401 in JS | user not logged in on that browser |
| `JavaScript interop calls cannot be issued at this time` | interop called in `OnInitialized` — move to `OnAfterRenderAsync` |
