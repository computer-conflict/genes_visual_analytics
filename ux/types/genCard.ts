export type genCard = {
  id: String
  name: String
  description: String
}

export function setGenCards(data: any): Array<genCard> | null {
  if (data == null || data.length <= 0) {
    return null
  }
  return data.map((item: any) => {
    return setGenCard(item)
  })
}

export function setGenCard(data: any): genCard | null {
  if (data == null || Object.keys(data).length <= 0) {
    return null
  }
  
  return {
    id: data.ids,
    name: data.metadatas.name,
    description: data.documents
  }
}