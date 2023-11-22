import mitt from 'mitt'


type ApplicationEvents = {
  'configuration:section': {section: string}
};

const emitter = mitt<ApplicationEvents>()

export const useEvent = emitter.emit
export const useListen = emitter.on
export const useOff = emitter.off
