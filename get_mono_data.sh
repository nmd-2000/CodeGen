python -m codegen_sources.preprocessing.preprocess \
/media/Z/dungnm31/unsafe_safe_rust/mono_data/ \
--langs unsafe safe \
--mode monolingual \
--local True \
--bpe_mode fast \
--train_splits 1 \
--keep_comments True