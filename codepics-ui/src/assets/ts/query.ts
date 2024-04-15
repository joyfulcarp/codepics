import axios from 'axios'

let url = import.meta.env.VITE_BACKEND_URL

export function getUrl() { return url }

export function getGames() {
  const path = url + 'games'
  return axios.get(path)
}

export function getCardCollections() {
  let collections = []
  const path = url + 'card_collections'
  return axios.get(path)
}

export function postCreateGame(event) {
  const path = url + 'create_game'
  return axios.post(path)
}
