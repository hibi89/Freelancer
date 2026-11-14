/** Read-only offline candidate model preflight; never downloads or runs arbitrary weights. */
import {preflightKoreanEmbedding} from '../enterprise/p85-korean-model-preflight.mjs';
const args=process.argv.slice(2);
if(args.length!==2||args[0]!=='--model-dir'){
  process.stderr.write('Usage: node scripts/p85-korean-model-check.mjs --model-dir ABSOLUTE_LOCAL_DIR\n');
  process.exitCode=2;
}else{
  try{const result=await preflightKoreanEmbedding({modelDir:args[1]});
    process.stdout.write(JSON.stringify(result)+'\n');
  }catch(e){process.stderr.write(JSON.stringify({ok:false,error:e?.code||'MODEL_CHECK_FAILED'})+'\n');
    process.exitCode=1;}
}
