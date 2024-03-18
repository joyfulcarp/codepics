import { io } from 'socket.io-client'
import type { Ref } from 'vue'

export interface TeamInfo {
  [members: number]: string
  cards: string
}

export interface Teams {
  blue: TeamInfo
  red: TeamInfo
}

export interface GameState {
  id: number
  lobby_state: string
  teams: Teams
}

interface GameUpdate {
  game: GameState
}

export class GameEvents {
  socket: io
  game: Ref<GameState>

  constructor(url: string, game: Ref<GameState>) {
    this.socket = io(url)
    this.game = game

    this.registerDebugEvents()
    this.registerEvents()
  }

  registerDebugEvents() {
    this.socket.onAny((eventName, ...args) => {
      console.log(eventName)
      console.log(args)
    })
    this.socket.onAnyOutgoing((eventName, ...args) => {
      console.log(eventName)
      console.log(args)
    })
  }

  registerEvents() {
    this.socket.on("update_game", (data) => this.updateGame(data))
    this.socket.on("update_teams",  (data) => this.updateTeams(data))
  }

  join(gameId: number, name: string) {
    this.socket.emit('join', {
      'game_id': gameId,
      'name': name
    })
  }

  leave(gameId: number) {
    this.socket.emit('leave', {'game_id': gameId})
  }

  joinTeam(gameId: number, team: string) {
    this.socket.emit('switch_team', {
      'game_id': gameId,
      'team': team
    })
  }

  updateGame(data: GameUpdate) {
    this.game.value = data.game
  }

  updateTeams(data: GameUpdate)  {
    this.game.value.teams = data.game.teams
  }
}
