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

export class GameEvents {
  socket: io
  game: Ref<GameState>

  constructor(url: string, game: Ref<GameState>) {
    this.socket = io(url)
    this.game = game

    this.registerDebugEvents()
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
}
