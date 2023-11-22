import { setGenCard, setGenCards } from '~~/types/genCard';


const functionsMap : any = {
  genCard: setGenCard,
  genCards: setGenCards
}

export function transformResponse(model:string, data:any): any {
  if(data === undefined || data === null) return data;

  // Transform to easier format
  const fields = Object.keys(data)
  const transformedData: Array<Object> = []
  data.ids[0].forEach((_value: any, index: string | number) => {
    const newEntries: any = {}
    fields.forEach(key => {
      newEntries[key] = data[key] === null ? undefined : data[key][0][index]
    })
    transformedData.push(newEntries)
  });
  
  try {
    if (Array.isArray(transformedData)) {
      return functionsMap[model](transformedData);
    } else {
      return functionsMap[`${model.slice(0, -1)}`](transformedData);
    }
  } catch (error) {
    console.log(error);
    return transformedData;
  }
}
