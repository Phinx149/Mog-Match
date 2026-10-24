---
name: realtime-chat
description: Build or debug MogMatch's real-time text chat between matched users using ASP.NET Core SignalR and Blazor. Use for ChatHub, ChatWindow, the chat page, sending/receiving messages, typing indicators, online status, or "messages don't show up live".
---

# Realtime Chat (SignalR)

Files: `src/MogMatch.Web/Hubs/ChatHub.cs`, `Components/Shared/ChatWindow.razor`, `Components/Pages/Chat.razor` (`@page "/chat/{MatchId:guid}"`), `Services/ChatService.cs`.

## Setup (Program.cs)
```csharp
builder.Services.AddSignalR();
builder.Services.AddScoped<ChatService>();
// ...
app.MapHub<ChatHub>("/hubs/chat");
```

## Hub
```csharp
[Authorize]
public class ChatHub(ChatService chat) : Hub
{
    private string UserId => Context.UserIdentifier!;      // from the auth cookie, trusted

    public async Task JoinMatch(Guid matchId)
    {
        if (!await chat.IsMemberAsync(matchId, UserId)) throw new HubException("Not your match");
        await Groups.AddToGroupAsync(Context.ConnectionId, $"match-{matchId}");
    }

    public async Task SendMessage(Guid matchId, string body)
    {
        body = body.Trim();
        if (body.Length is 0 or > 4000) return;
        if (!await chat.IsMemberAsync(matchId, UserId)) throw new HubException("Not your match");

        var msg = await chat.SaveAsync(matchId, UserId, body);   // persist first
        await Clients.Group($"match-{matchId}").SendAsync("ReceiveMessage", msg);
    }

    public Task Typing(Guid matchId) =>
        Clients.OthersInGroup($"match-{matchId}").SendAsync("UserTyping", UserId);
}
```
`msg` should be a small DTO record (`MessageDto(long Id, Guid SenderId, string Body, DateTime CreatedAt)`), not the EF entity.

## Blazor component
```razor
@implements IAsyncDisposable
@inject NavigationManager Nav
@inject ChatService Chat
@inject IHttpContextAccessor HttpContextAccessor

@foreach (var m in messages)
{
    <div class="@(m.SenderId == MyProfileId ? "text-end" : "text-start")">@m.Body</div>
}
<input @bind="draft" @bind:event="oninput" @onkeydown="OnKey" class="form-control" />

@code {
    [Parameter] public Guid MatchId { get; set; }
    [Parameter] public Guid MyProfileId { get; set; }
    private readonly List<MessageDto> messages = [];
    private HubConnection? hub;
    private string draft = "";

    protected override async Task OnInitializedAsync()
    {
        messages.AddRange(await Chat.GetRecentAsync(MatchId, take: 50));

        hub = new HubConnectionBuilder()
            .WithUrl(Nav.ToAbsoluteUri("/hubs/chat"), o =>
            {
                // Blazor Server: forward the user's auth cookie to the hub
                var cookies = HttpContextAccessor.HttpContext?.Request.Cookies;
                if (cookies is not null)
                    foreach (var c in cookies) o.Cookies.Add(new Cookie(c.Key, c.Value, "/", Nav.ToAbsoluteUri("/").Host));
            })
            .WithAutomaticReconnect()
            .Build();

        hub.On<MessageDto>("ReceiveMessage", m =>
        {
            if (messages.All(x => x.Id != m.Id)) messages.Add(m);
            InvokeAsync(StateHasChanged);          // hub callbacks run off the UI thread
        });

        await hub.StartAsync();
        await hub.InvokeAsync("JoinMatch", MatchId);
    }

    private async Task OnKey(KeyboardEventArgs e)
    {
        if (e.Key != "Enter" || string.IsNullOrWhiteSpace(draft) || hub is null) return;
        var text = draft; draft = "";
        await hub.InvokeAsync("SendMessage", MatchId, text);
    }

    public async ValueTask DisposeAsync() { if (hub is not null) await hub.DisposeAsync(); }
}
```
Needs `builder.Services.AddHttpContextAccessor();`. The cookie must be captured during the initial (prerendered) request — if `HttpContext` is null, pass the cookie in from `Chat.razor` as a cascading value instead.

**Simpler alternative if the cookie forwarding fights you:** since Interactive Server runs every circuit on the same server, a singleton `ChatNotifier` with a C# `event Action<Guid, MessageDto>` works for a single-instance hackathon deploy. Keep the hub anyway for voice signaling (browser JS connects to it directly).

## Debugging checklist
1. Browser devtools → Network → WS: is there a connection to `/hubs/chat`? 401 → auth cookie not forwarded.
2. Did `JoinMatch` throw? Check the server console for `HubException`.
3. UI doesn't update → missing `InvokeAsync(StateHasChanged)`.
4. Messages appear twice → component subscribed twice; dispose the connection in `DisposeAsync`, and dedupe by `Id`.

## Extras
- **Typing indicator:** call `Typing` on input (throttle to once per 2s), show "typing…" for 3s after `UserTyping`.
- **Online status:** track connections in `OnConnectedAsync`/`OnDisconnectedAsync` with a singleton `ConcurrentDictionary`.
- **Auto-scroll:** small JS interop `element.scrollIntoView()` after render.
- **Safety:** Razor HTML-encodes `@m.Body` automatically. Never render message text with `MarkupString`.
- **Header:** other user's avatar + the match's Team Mog Score.
